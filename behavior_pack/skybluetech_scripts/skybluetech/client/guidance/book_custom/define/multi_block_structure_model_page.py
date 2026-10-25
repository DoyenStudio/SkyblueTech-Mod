# coding=utf-8
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    StructureBlockPalette,
)

from .base_page import BasePage
from .multi_block_structure_render_page import generate_blocks_btn_callback
from .structure_model_projection import StructureModelProjection


class MultiBlockStructureModelPage(BasePage):
    ctrl_def_name = "GuidanceLib.multi_block_structure_model_page"

    def __init__(self, center_block_id, palette):
        # type: (str, StructureBlockPalette) -> None
        BasePage.__init__(self)
        self.center_block_id = center_block_id
        self.palette = palette
        self._ctrl = None
        self._drag = None
        self._size_slider = None

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        self._ctrl = ctrl
        self._blocks = self._get_display_blocks()
        self._layers = sorted(set(pos[1] for pos in self._blocks))
        self._views = [None] + self._layers
        self._view_index = 0
        # 缓存仅属于本次打开的页面，换层不重复合并模型。
        self._models = {}
        self._callbacks = {}
        self._drag = None
        self._render_ok = False
        self._indices = {
            pos: index for index, positions in self.palette.posblock_data.items()
            for pos in positions
        }
        self._indices[(0, 0, 0)] = -1
        size = max(
            max(pos[axis] for pos in self._blocks)
            - min(pos[axis] for pos in self._blocks) + 1
            for axis in range(3)
        )
        self._base_scale = 6.0 / size
        self._projection = StructureModelProjection(self._base_scale)
        self._size_progress = 0.5
        self._renderer = ctrl["structure_model_input/model_clip/model"].asNeteasePaperDoll()
        self._size_slider = ctrl["size_ctrl_slider"].asSlider()
        self._mouse = CF.CreateActorMotion(GetLocalPlayerId())
        button = ctrl["structure_model_input"].asButton().base
        button.AddTouchEventParams({"isSwallow": True})
        button.SetButtonTouchDownCallback(self._on_press)
        button.SetButtonTouchMoveCallback(self._on_move)
        button.SetButtonTouchUpCallback(self._on_release)
        button.SetButtonTouchCancelCallback(self._on_cancel)
        ctrl["add_layer_btn"].asButton().SetCallback(self._next_layer)
        ctrl["sub_layer_btn"].asButton().SetCallback(self._previous_layer)
        self._show_view()
        self._size_slider.SetSliderValue(0.5)
        ctrl["size_ctrl_text"].asLabel().SetText("100%%")

    def UpdateSizeFromSlider(self):
        if self._size_slider is None:
            return
        progress = max(0.0, min(1.0, self._size_slider.GetSliderValue()))
        if abs(progress - self._size_progress) < 1e-6:
            return
        self._size_progress = progress
        # 等比缩放：滑块 0 / 0.5 / 1 对应模型 25% / 100% / 400%。
        zoom = 4.0 ** (2.0 * progress - 1.0)
        self._projection.scale = self._base_scale * zoom
        self._ctrl["size_ctrl_text"].asLabel().SetText(
            "%d%%%%" % int(round(zoom * 100))
        )
        self._drag = None
        self._close_block_popup()
        self._render_model()

    def _show_view(self):
        self._close_block_popup()
        self._drag = None
        layer = self._views[self._view_index]
        self._ctrl["layer_label"].asLabel().SetText(
            "预览全部" if layer is None else "第 %d 层" % (self._layers.index(layer) + 1)
        )
        self._projection.set_positions([
            pos for pos in self._blocks if layer is None or pos[1] == layer
        ])
        if layer not in self._models:
            geometry_id = self._create_geometry(self._blocks, layer)
            if geometry_id is not None:
                self._models[layer] = geometry_id
        self._geometry_id = self._models.get(layer)
        self._render_model()

    def _render_model(self):
        self._render_ok = False
        if self._geometry_id is not None:
            self._renderer.SetVisible(True)
            self._render_ok = self._renderer.RenderBlockGeometryModel(
                self._geometry_id,
                scale=self._projection.scale,
                # 零旋转沿竖直轴观察，-90 度将侧面校正为正立。
                init_rot_x=self._projection.pitch,
                init_rot_y=0,
                init_rot_z=self._projection.yaw,
                rotation_axis=(0, 0, 0),
            )
        self._renderer.SetVisible(self._render_ok)
        self._ctrl["error"].SetVisible(not self._render_ok)

    def _next_layer(self, _):
        self._view_index = (self._view_index + 1) % len(self._views)
        self._show_view()

    def _previous_layer(self, _):
        self._view_index = (self._view_index - 1) % len(self._views)
        self._show_view()

    def _on_press(self, args):
        if self._render_ok:
            self._drag = (
                (args["TouchPosX"], args["TouchPosY"]),
                self._projection.pitch, self._projection.yaw,
            )
            self._drag_moved = False

    def _move_to(self, point):
        if self._drag is None:
            return
        start, pitch, yaw = self._drag
        dx, dy = point[0] - start[0], point[1] - start[1]
        if dx * dx + dy * dy > 9:
            self._drag_moved = True
        if not self._drag_moved:
            return
        new_pitch, new_yaw = pitch + dy, (yaw - dx) % 360.0
        if (new_pitch, new_yaw) != (self._projection.pitch, self._projection.yaw):
            self._projection.pitch, self._projection.yaw = new_pitch, new_yaw
            self._render_model()

    def _on_move(self, args):
        self._move_to((args["TouchPosX"], args["TouchPosY"]))

    def ScreenTicking(self):
        # PC 不发送 TouchMove；鼠标位置与 TouchPos、UI 控件使用相同坐标单位。
        if self._drag is not None:
            point = self._mouse.GetMousePosition()
            if point is not None:
                self._move_to(point)

    def _on_release(self, args):
        if self._drag is None:
            return
        point = (args["TouchPosX"], args["TouchPosY"])
        self._move_to(point)
        clicked = not self._drag_moved
        self._drag = None
        if not clicked or not self._render_ok:
            return
        pos = self._projection.pick(
            point, self._renderer.GetRootPos(), self._renderer.GetSize()
        )
        if pos is not None:
            self._close_block_popup()
            generate_blocks_btn_callback(
                self._ctrl, self.palette, self._indices[pos],
                self._callbacks, self.center_block_id,
            )(args)
            popup = self._ctrl._vars["block_stack_desc"]
            popup["exit_btn"].asButton().SetCallback(self._close_block_popup)

    def _on_cancel(self, _):
        self._drag = None

    def _close_block_popup(self, _=None):
        if self._ctrl is not None:
            popup = self._ctrl._vars.pop("block_stack_desc", None)
            if popup is not None:
                popup.Remove(warning=False)

    def DeRender(self, ctrl):
        self._close_block_popup()
        self._drag = None
        self._ctrl = None
        self._renderer = None
        self._size_slider = None
        self._mouse = None
        self._callbacks = {}

    def _get_display_blocks(self):
        # type: () -> dict[tuple[int, int, int], str]
        blocks = {}
        for index, block_ids in self.palette.palette_data.items():
            # 可选位置以首个候选方块展示；弹窗列出该位置全部候选。
            block_id = block_ids if isinstance(block_ids, str) else block_ids[0]
            if block_id == "minecraft:air":
                continue
            for pos in self.palette.posblock_data[index]:
                blocks[pos] = block_id
        # 检测调色板不含控制器，预览必须补上。
        blocks[(0, 0, 0)] = self.center_block_id
        return blocks

    def _create_geometry(self, blocks, layer):
        # type: (dict[tuple[int, int, int], str], int | None) -> str | None
        selected = {
            pos: block_id for pos, block_id in blocks.items()
            if layer is None or pos[1] == layer
        }
        min_x = min(pos[0] for pos in selected)
        min_y = min(pos[1] for pos in selected)
        min_z = min(pos[2] for pos in selected)
        size_x = max(pos[0] for pos in selected) - min_x + 1
        size_y = max(pos[1] for pos in selected) - min_y + 1
        size_z = max(pos[2] for pos in selected) - min_z + 1
        common = {}
        for (x, y, z), block_id in sorted(selected.items()):
            index = (y - min_y) * size_x * size_z + (x - min_x) * size_z + z - min_z
            common.setdefault((block_id, 0), []).append(index)
        block_palette = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
        if block_palette is None:
            return None
        if not block_palette.DeserializeBlockPalette({
            "extra": {},
            "void": False,
            "actor": {},
            # 原生序列化使用 (z, x, y)，与 GetVolumeOfBlockPalette 不同。
            "volume": (size_z, size_x, size_y),
            "common": common,
            "eliminateAir": True,
        }):
            return None
        # 每个页面、每种视图使用固定名称，重开时覆盖，避免不断生成新资源。
        geometry_name = "geometry.skybluetech.guidance.%s.%s" % (
            id(self), "all" if layer is None else "layer_%d" % layer
        )
        return CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
            block_palette, geometry_name
        )
