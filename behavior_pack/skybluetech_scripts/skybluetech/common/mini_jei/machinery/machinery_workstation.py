# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from ....common.define.id_enum import machinery, items
from ....common.define.tag_enum import Wrench, Pincer
from .render_utils import ItemDisplayer, InputDisplayer, MultiItemsDisplayer
from .recipe_cls import CategoryType, Recipe, Input, Output


class MachineryWorkstationRecipe(Recipe):
    recipe_icon_id = machinery.MACERATOR
    render_ui_def_name = "RecipeCheckerUI.machinery_workstation_recipes"

    LEVEL_IRON = 1
    LEVEL_INVAR = 2
    LEVEL_MAPPING = {
        LEVEL_IRON: "铁",
        LEVEL_INVAR: "殷钢",
    }

    def __init__(
        self, input_items, output_item_id, wrench_level, pincer_level, craft_times
    ):
        # type: (dict[int, Input], str, int, int, int) -> None
        Recipe.__init__(
            self,
            {CategoryType.ITEM: input_items},
            {CategoryType.ITEM: {0: Output(output_item_id)}},
        )
        self.input_items = input_items
        self.output_item_id = output_item_id
        self.wrench_level = wrench_level
        self.pincer_level = pincer_level
        self.craft_times = craft_times

    def GetInputs(self):
        orig = Recipe.GetInputs(self)
        return orig

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self.dyn_item_renders = []  # type: list[InputDisplayer | MultiItemsDisplayer]
        input_items = self.inputs.get("item", {})
        for slot, input in input_items.items():
            self.dyn_item_renders.append(InputDisplayer(panel["slot%d" % slot], input))
        if self.wrench_level > 0:
            self.dyn_item_renders.append(
                MultiItemsDisplayer(
                    panel["wrench_slot"],
                    get_spec_level_avail_wrenchs(self.wrench_level),
                )
            )
        if self.pincer_level > 0:
            self.dyn_item_renders.append(
                MultiItemsDisplayer(
                    panel["pincer_slot"],
                    get_spec_level_avail_pincers(self.pincer_level),
                )
            )
        ItemDisplayer(panel["output_slot"], Item(self.output_item_id))
        panel["level_tip"].asLabel().SetText(
            "扳手等级： %s\n钳等级： %s"
            % (
                self.LEVEL_MAPPING[self.wrench_level],
                self.LEVEL_MAPPING[self.pincer_level],
            )
        )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        for input_render in self.dyn_item_renders:
            input_render.tick(render_ticks)


PINCER_LEVEL2ITEM = {
    MachineryWorkstationRecipe.LEVEL_IRON: items.Pincer.IRON,
}
WRENCH_LEVEL2ITEM = {
    MachineryWorkstationRecipe.LEVEL_IRON: items.Wrench.IRON,
}


def get_wrench_level(wrench_item):
    # type: (Item) -> int
    tags = wrench_item.GetBasicInfo().tags
    if Wrench.INVAR in tags:
        return MachineryWorkstationRecipe.LEVEL_INVAR
    elif Wrench.IRON in tags:
        return MachineryWorkstationRecipe.LEVEL_IRON
    return 0


def get_pincer_level(pincer_item):
    # type: (Item) -> int
    tags = pincer_item.GetBasicInfo().tags
    if Pincer.INVAR in tags:
        return MachineryWorkstationRecipe.LEVEL_INVAR
    elif Pincer.IRON in tags:
        return MachineryWorkstationRecipe.LEVEL_IRON
    return 0


def get_spec_level_avail_wrenchs(level):
    # type: (int) -> list[Item]
    return [Item(v) for k, v in WRENCH_LEVEL2ITEM.items() if k >= level]


def get_spec_level_avail_pincers(level):
    # type: (int) -> list[Item]
    return [Item(v) for k, v in PINCER_LEVEL2ITEM.items() if k >= level]
