# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl, UImage
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from skybluetech_scripts.tooldelta.utils.nbt import (
    GetValueWithDefault as GetValue,
    NBT2Py,
)
from skybluetech_scripts.skybluetech.common.define.fluids import (
    texture as fluid_texture,
)
from skybluetech_scripts.skybluetech.common.define.fluids.define import (
    BasicFluidTexture,
)
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Gas
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STRUCTURE_LACKED_BLOCKS,
    K_STRUCTURE_LACKED_BLOCK_POSES,
)

# TYPE_CHECKING
if 0>1:
    import typing

    T = typing.TypeVar("T")
    BtnCb = typing.Callable[[], T]
# TYPE_CHECKING END

INFINITY = float("inf")

FLUID_SMOOTH_FACTOR = 0.05
FLUID_SMOOTH_EPSILON = 0.001
FLUID_FRAME_SIZE = 16


def FormatNum(n, fmt="%.2f %s"):
    # type: (float, str) -> str
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    if n == INFINITY:
        return "无限"
    while d < len(suffixes) and n >= 1000:
        d += 1
        n /= 1000.0
    return fmt % (n, suffixes[d])


def FormatRF(rf):
    # type: (float) -> str
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    if rf == INFINITY:
        return "无限 RF"
    while d < len(suffixes) and rf >= 1000:
        d += 1
        rf /= 1000.0
    return "%.2f %sRF" % (rf, suffixes[d])


def FormatFluidVolume(vol):
    # type: (float) -> str
    if vol == INFINITY:
        return "无限"
    elif vol >= 10000:
        return "%.2f B" % (float(vol) / 1000)
    else:
        return "%.0f mB" % vol


def FormatKelvin(k):
    # type: (float) -> str
    if k == INFINITY:
        return "Inf"
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    while d < len(suffixes) and k >= 1000:
        d += 1
        k /= 1000.0
    return "%.2f %sK" % (k, suffixes[d])


def UpdatePowerBar(ui, rf_now, rf_max):
    # type: (UBaseCtrl, int, int) -> None
    if rf_max <= 0:
        return
    top = ui["bar/mask"]
    label = ui["label"]
    top.SetFullSize(
        "y", UICtrlPosData("parent", relative_value=min(2, float(rf_now) / rf_max))
    )
    label.asLabel().SetText(FormatRF(rf_now))


def UpdateFlame(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromTopToBottom", 1 - percent)


def UpdateGenericProgressL2R(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - percent)


def UpdateGenericProgressT2B(ui, percent):  # -> Any:
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromTopToBottom", 1 - percent)


def UpdateGenericProgressB2T(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromBottomToTop", 1 - percent)


def GetStructureLackedBlocks(data):
    # type: (dict) -> dict[str, int]
    lacked_blocks = NBT2Py(data.get(K_STRUCTURE_LACKED_BLOCKS, {}))
    if isinstance(lacked_blocks, dict) and lacked_blocks:
        return {str(k): int(v) for k, v in lacked_blocks.items()}
    return {}


def GetStructureLackedBlockPoses(data):
    # type: (dict) -> list[dict]
    """从方块实体数据中解析缺失方块的具体位置列表."""
    raw = NBT2Py(data.get(K_STRUCTURE_LACKED_BLOCK_POSES, []))
    poses = []
    if not isinstance(raw, list):
        return poses
    for item in raw:
        if not isinstance(item, dict):
            continue
        x = item.get("x")
        y = item.get("y")
        z = item.get("z")
        if x is None or y is None or z is None:
            continue
        expected = item.get("expected")
        if isinstance(expected, str):
            expected = [expected]
        if not isinstance(expected, list):
            continue
        actual = item.get("actual")
        poses.append({
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "expected": [str(v) for v in expected],
            "actual": str(actual) if actual else "",
        })
    return poses


def FormatStructureLackedBlockPoses(poses):
    # type: (list[dict]) -> str
    """将缺失方块位置列表格式化为 '(x, y, z) 应为xxx, 目前xxx' 的多行文本."""
    lines = []
    for pose in poses:
        expected = " / ".join(
            (GetItemHoverName(v) or v).replace("§r", "").replace("§f", "")
            for v in pose["expected"]
        )
        actual_id = pose.get("actual") or ""
        if not actual_id or actual_id == "minecraft:air":
            actual = "空气"
        else:
            actual = (GetItemHoverName(actual_id) or actual_id).replace(
                "§r", ""
            ).replace("§f", "")
        lines.append(
            "(%d, %d, %d) 应为%s, 当前为%s"
            % (pose["x"], pose["y"], pose["z"], expected, actual)
        )
    return "\n".join(lines)


def UpdateImageTransformColor(
    img, raw_r, raw_g, raw_b, new_r, new_g, new_b, transform_pc
):
    # type: (UImage, float, float, float, float, float, float, float) -> None
    r = raw_r + (new_r - raw_r) * transform_pc
    g = raw_g + (new_g - raw_g) * transform_pc
    b = raw_b + (new_b - raw_b) * transform_pc
    img.SetSpriteColor((r / 255, g / 255, b / 255))


class FluidDisplayer(object):
    def __init__(self, ctrl, enable_interact=True):
        # type: (UBaseCtrl, bool) -> None
        self.ctrl = ctrl
        self.databoard = None
        self.fluid_id = None
        self.fluid_volume = None
        self.max_volume = None
        self.rendered_display_fluid_id = None
        self.rendered_display_fluid_relative_volume = 0.0
        self.flipbook_frame = 0
        self.flipbook_tick = 0
        self.first_update = True
        self.enable_interact = enable_interact
        btn = ctrl["data_btn"].asButton()
        screen_vars = ctrl._root._vars

        if not enable_interact:
            return

        # def onRollOver(params):
        #     prev_board = get_last_ui_board()
        #     if prev_board is not None:
        #         return
        #     e = ctrl._root.AddElement("SkybluePanelLib.DataTextScreen", "fluid_hover_text")
        #     e.SetPos(ctrl.GetRootPos())
        #     e.SetLayer(100)
        #     screen_vars["disp_fluid_databoard"] = e
        #     current_ctrl[0] = e
        #     _updateHook()

        # def onRollOut(params):
        #     prev_board = get_last_ui_board()
        #     if prev_board is not None:
        #         prev_board.Remove()
        #         del screen_vars["disp_fluid_databoard"]
        #     current_ctrl[0] = None

        def onRelease(params):
            prev_board = ctrl._root._vars.get("disp_board")  # type: UBaseCtrl | None
            if prev_board is not None:
                prev_board.Remove()
                del screen_vars["disp_board"]
                if screen_vars.get("disp_board_src") is ctrl:
                    screen_vars.pop("disp_board_src")
                    return
            e = ctrl._root.AddElement(
                "SkybluePanelLib.DataTextScreen", "fluid_hover_text"
            )
            e.SetPos(ctrl.GetRootPos())
            e.SetLayer(100)
            screen_vars["disp_board"] = e
            screen_vars["disp_board_src"] = ctrl
            self._update_hover()

        # btn.SetOnRollOverCallback(onRollOver)
        # btn.SetOnRollOutCallback(onRollOut)
        btn.SetCallback(onRelease)

    def update(self, fluid_id, fluid_volume, max_volume):
        # type: (str | None, float, float) -> None
        self.fluid_id = fluid_id
        self.fluid_volume = fluid_volume
        self.max_volume = max_volume

        self.ctrl["text"].asLabel().SetText(
            "%s / %s"
            % (
                FormatFluidVolume(fluid_volume),
                FormatFluidVolume(max_volume),
            )
        )
        self._update_fluid_img()
        if self.enable_interact:
            self._update_hover()

    def _get_target_relative_volume(self):
        # type: () -> float
        if (
            self.fluid_id is None
            or self.fluid_volume is None
            or self.max_volume is None
        ):
            return 0.0
        elif self.fluid_volume == INFINITY:
            return 1.0
        elif self.max_volume == INFINITY:
            return 0.0
        return float(self.fluid_volume) / self.max_volume

    def _update_fluid_img(self):
        # type: () -> None
        fluid_img = self.ctrl["fluid/img"].asImage()
        target = self._get_target_relative_volume()

        if self.first_update:
            self.first_update = False
            self.rendered_display_fluid_id = self.fluid_id
            rendered = target
        else:
            if self.fluid_id != self.rendered_display_fluid_id:
                if self.rendered_display_fluid_relative_volume <= FLUID_SMOOTH_EPSILON:
                    self.rendered_display_fluid_id = self.fluid_id
                    self.flipbook_frame = 0
                    self.flipbook_tick = 0
                else:
                    target = 0.0
            rendered = self.rendered_display_fluid_relative_volume
            rendered += (target - rendered) * FLUID_SMOOTH_FACTOR
            if abs(target - rendered) <= FLUID_SMOOTH_EPSILON:
                rendered = target
        self.rendered_display_fluid_relative_volume = rendered

        rendered_fluid_id = self.rendered_display_fluid_id
        if rendered_fluid_id is None:
            fluid_img.SetFullSize("y", UICtrlPosData("parent", relative_value=0))
            return

        texture = fluid_texture.GetFluidTexture(rendered_fluid_id)
        fluid_img.SetSprite(texture.basic_texture.texture_path)
        r, g, b = texture.rgb
        fluid_img.SetSpriteColor((float(r) / 255, float(g) / 255, float(b) / 255))
        fluid_img.SetAlpha(float(texture.alpha) / 255)
        self._update_flipbook(fluid_img, texture.basic_texture)

        if rendered_fluid_id in Gas.all_sub():
            fluid_img.SetAnchorFrom("top_middle")
            fluid_img.SetAnchorTo("top_middle")
        else:
            fluid_img.SetAnchorFrom("bottom_middle")
            fluid_img.SetAnchorTo("bottom_middle")
            fluid_img.SetFullPos("y", UICtrlPosData("none", relative_value=0))
        fluid_img.SetFullSize(
            "y", UICtrlPosData("parent", relative_value=min(2, rendered))
        )

    def _update_flipbook(self, fluid_img, basic_texture):
        # type: (UImage, BasicFluidTexture) -> None
        if basic_texture.flipbook_frames > 1:
            self.flipbook_tick += 1
            if self.flipbook_tick >= basic_texture.ticks_per_frame:
                self.flipbook_tick = 0
                self.flipbook_frame = (
                    self.flipbook_frame + 1
                ) % basic_texture.flipbook_frames
        fluid_img.SetUV(
            (0, self.flipbook_frame * FLUID_FRAME_SIZE),
            (FLUID_FRAME_SIZE, FLUID_FRAME_SIZE),
        )

    def _update_hover(self):
        # type: () -> None
        databoard = self.ctrl._root._vars.get("disp_board")  # type: UBaseCtrl | None
        databoard_src = self.ctrl._root._vars.get("disp_board_src")  # type: UBaseCtrl | None
        if databoard is None or databoard_src is not self.ctrl:
            return
        (databoard / "image/label").asLabel().SetText(
            "§d流体类型： §f"
            + (
                (GetItemHoverName(self.fluid_id) or self.fluid_id)
                if self.fluid_id is not None
                else ("未知" if self.max_volume is None else "空")
            )
            + "\n"
            + "§a体积： §f"
            + (
                FormatFluidVolume(self.fluid_volume)
                if self.fluid_volume is not None
                else "未知"
            )
            + "\n"
            + "§6容器体积： §f"
            + (
                FormatFluidVolume(self.max_volume)
                if self.max_volume is not None
                else "未知"
            )
        )
