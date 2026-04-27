# coding=utf-8
import math
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    StructureBlockPalette,
)
from .base_page import BasePage

if 0:
    import typing  # noqa: F401


class MultiBlockStructureRenderPage(BasePage):
    ctrl_def_name = "GuidanceLib.multi_block_structure_render_page"

    def __init__(self, center_block_id, palette):
        # type: (str, StructureBlockPalette) -> None
        self.center_block_id = center_block_id
        self.palette = palette
        self.current_ticker = None

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None

        BasePage.RenderInit(self, ctrl)
        env = local_env()
        layer_blocks_renderers = {}  # type: dict[int, list[UBaseCtrl]]
        content = ctrl["scroll_view"].asScrollView().GetContent()
        add_layer_btn = ctrl["add_layer_btn"].asButton()
        sub_layer_btn = ctrl["sub_layer_btn"].asButton()
        layer_label = ctrl["layer_label"].asLabel()

        cacher = {}

        def render_block(palette_index, block_id, x, y, z):
            # type: (int, str, int, int, int) -> UBaseCtrl
            env.render_counter += 1
            block_renderer = content.AddElement(
                "SkybluePanelLib.ui_block_stack_renderer",
                "block_renderer%d" % env.render_counter,
            ).asButton()
            px, py = xyz_to_xy(x, y, z)
            block_renderer.SetPos((px + 100, 100 - py))
            block_renderer.SetLayer(50 + x + y - z)  # TODO
            block_renderer["renderer"].asItemRenderer().SetUiItem(Item(block_id))
            block_renderer.SetCallback(
                generate_blocks_btn_callback(
                    ctrl, self.palette, palette_index, cacher, self.center_block_id
                )
            )
            return block_renderer

        def change_layer(now=None):
            # type: (int | None) -> None
            prev = env.current_render_layer
            env.current_render_layer = now
            if prev is None and now is None:
                # error
                return
            if prev is None:
                for layer, renderers in layer_blocks_renderers.items():
                    if layer != now:
                        for renderer in renderers:
                            renderer.SetVisible(False)
                layer_label.SetText("第 %d 层" % now)
            elif now is None:
                for layer, renderers in layer_blocks_renderers.items():
                    if layer != now:
                        for renderer in renderers:
                            renderer.SetVisible(True)
                layer_label.SetText("预览全部")
            else:
                for renderer in layer_blocks_renderers.get(prev, []):
                    renderer.SetVisible(False)
                for renderer in layer_blocks_renderers.get(now, []):
                    renderer.SetVisible(True)
                layer_label.SetText("第 %d 层" % now)

        def async_render():
            for palette_index, block_id_or_ids in self.palette.palette_data.items():
                poses = self.palette.posblock_data[palette_index]
                for x, y, z in poses:
                    if isinstance(block_id_or_ids, str):
                        block_id = block_id_or_ids
                        block_renderer = render_block(palette_index, block_id, x, y, z)
                    else:
                        block_id = block_id_or_ids[0]
                        block_renderer = render_block(palette_index, block_id, x, y, z)
                        env.carouselers.append(
                            block_carouseler(block_renderer, block_id_or_ids)
                        )
                    layer_blocks_renderers.setdefault(y, []).append(block_renderer)
                    yield

        core_renderer = render_block(-1, self.center_block_id, 0, 0, 0)
        layer_blocks_renderers.setdefault(0, []).append(core_renderer)
        render_iterator = async_render()

        def tick_render():
            env.tick_counter += 1
            if env.tick_counter % 30 == 0:
                for carouseler in env.carouselers:
                    carouseler.update()
            try:
                next(render_iterator)
            except StopIteration:
                pass

        def on_add_layer(_):
            layer = env.current_render_layer
            if layer is None:
                layer = min(layer_blocks_renderers.keys()) - 1
            new_layer = layer + 1
            if new_layer not in layer_blocks_renderers:
                return
            change_layer(new_layer)

        def on_sub_layer(_):
            layer = env.current_render_layer
            if layer is None:
                return
            new_layer = layer - 1
            if new_layer not in layer_blocks_renderers:
                new_layer = None
            change_layer(new_layer)

        add_layer_btn.SetCallback(on_add_layer)
        sub_layer_btn.SetCallback(on_sub_layer)
        self.current_ticker = tick_render

    def ScreenTicking(self):
        if self.current_ticker is not None:
            self.current_ticker()

    def DeRender(self, ctrl):
        self.current_ticker = None
        block_stack_desc = ctrl._vars.get("block_stack_desc")
        if block_stack_desc is not None:
            block_stack_desc.Remove()


RAD = math.atan(0.5)
CONTROL_WIDTH = 30
UPPER_EDGE_LENGTH = CONTROL_WIDTH / 2 / math.cos(RAD)
CENTER_EDGE_LENGTH = CONTROL_WIDTH - CONTROL_WIDTH * math.tan(RAD)


class local_env:
    def __init__(self):
        self.render_counter = 0
        self.tick_counter = 0
        self.carouselers = []  # type: list[block_carouseler]
        self.current_render_layer = None  # type: int | None


class block_carouseler:
    def __init__(self, block_ctrl, block_ids):
        # type: (UBaseCtrl, list[str]) -> None
        self.renderer = block_ctrl["renderer"].asItemRenderer()
        self.block_ids = block_ids
        self.idx = 0
        self.update()

    def update(self):
        self.idx = (self.idx + 1) % len(self.block_ids)
        self.renderer.SetUiItem(Item(self.block_ids[self.idx]))


def xyz_to_xy(x, y, z):
    # type: (int, int, int) -> tuple[float, float]
    return (
        -(x * (UPPER_EDGE_LENGTH - 2)) * math.cos(RAD)
        - (z * (UPPER_EDGE_LENGTH - 2)) * math.cos(RAD),
        -(x * (UPPER_EDGE_LENGTH - 2)) * math.sin(RAD)
        + (y * (CENTER_EDGE_LENGTH + 2))
        + (z * (UPPER_EDGE_LENGTH - 2)) * math.sin(RAD),
    )


block_recipe_cbs_cacher = {}


def generate_block_recipe_check_btn_cb(
    block_id,  # type: str
):
    from ....ui.recipe_checker import CheckRecipe

    cb = block_recipe_cbs_cacher.get(block_id)

    if cb is None:

        def on_click(_):
            CheckRecipe(block_id)
            return None

        res = block_recipe_cbs_cacher[block_id] = on_click
        return res
    else:
        return cb


def generate_blocks_btn_callback(
    ctrl,  # type: UBaseCtrl
    palette,  # type: StructureBlockPalette
    palette_index,  # type: int
    global_cacher,  # type: dict[int, typing.Callable[[typing.Any], None]]
    core_block_id,  # type: str
):

    cb = global_cacher.get(palette_index)
    if cb is not None:
        return cb
    if palette_index != -1:
        block_ids = palette.palette_data[palette_index]
    else:
        block_ids = [core_block_id]
    if isinstance(block_ids, str):
        block_ids = [block_ids]

    def on_click(_):
        e = ctrl._parent.AddElement(
            "SkybluePanelLib.ui_block_stack_desc", "ui_block_stack_desc"
        )
        e.SetLayer(80).BindLifeToObject(ctrl)
        e["exit_btn"].asButton().SetCallback(lambda _: e.Remove())
        grid = e["bg/grid"].asGrid()
        ctrl._vars["block_stack_desc"] = e

        def after():
            for i in range(len(block_ids)):
                block_id = block_ids[i]
                grid_elem = grid.GetGridItem(i, 0).asButton()
                grid_elem["item_renderer"].asItemRenderer().SetUiItem(Item(block_id))
                grid_elem.SetCallback(generate_block_recipe_check_btn_cb(block_id))

        grid.SetDimensionAndCall((len(block_ids), 1), after)

    global_cacher[palette_index] = on_click
    return on_click
