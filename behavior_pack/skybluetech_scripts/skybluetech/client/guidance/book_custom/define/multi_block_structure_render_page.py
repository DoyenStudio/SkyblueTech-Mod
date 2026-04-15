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

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None

        BasePage.RenderInit(self, ctrl)
        env = local_env()
        content = ctrl["scroll_view"].asScrollView().GetContent()
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

        def async_render():
            for palette_index, block_id_or_ids in self.palette.palette_data.items():
                poses = self.palette.posblock_data[palette_index]
                for x, y, z in poses:
                    if isinstance(block_id_or_ids, str):
                        block_id = block_id_or_ids
                        render_block(palette_index, block_id, x, y, z)
                    else:
                        block_id = block_id_or_ids[0]
                        block_renderer = render_block(palette_index, block_id, x, y, z)
                        env.carousels.append(
                            block_carouseler(block_renderer, block_id_or_ids)
                        )
                    yield

        render_block(-1, self.center_block_id, 0, 0, 0)
        render_iterator = async_render()

        def tick_render():
            env.tick_counter += 1
            if env.tick_counter % 30 == 0:
                for carousel in env.carousels:
                    carousel.update()
            try:
                next(render_iterator)
            except StopIteration:
                pass

        ctrl._root.AddOnTickingCallback(tick_render)


RAD = math.atan(0.5)
CONTROL_WIDTH = 30
UPPER_EDGE_LENGTH = CONTROL_WIDTH / 2 / math.cos(RAD)
CENTER_EDGE_LENGTH = CONTROL_WIDTH - CONTROL_WIDTH * math.tan(RAD)


class local_env:
    def __init__(self):
        self.render_counter = 0
        self.tick_counter = 0
        self.carousels = []  # type: list[block_carouseler]


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
        e.SetLayer(80)
        e["exit_btn"].asButton().SetCallback(lambda _: e.Remove())
        grid = e["bg/grid"].asGrid()

        def after():
            for i in range(len(block_ids)):
                block_id = block_ids[i]
                grid_elem = grid.GetGridItem(i, 0).asButton()
                grid_elem["item_renderer"].asItemRenderer().SetUiItem(Item(block_id))
                grid_elem.SetCallback(generate_block_recipe_check_btn_cb(block_id))

        grid.SetDimensionAndCall((len(block_ids), 1), after)

    global_cacher[palette_index] = on_click
    return on_click
