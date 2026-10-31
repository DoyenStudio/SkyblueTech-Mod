# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe,
    get_spec_level_avail_wrenchs,
    get_spec_level_avail_pincers,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer, CreateDescBoard
from skybluetech_scripts.skybluetech.common.mini_jei import CategoryType
from ...ui.recipe_checker.render_utils_advanced import (
    InputDisplayer,
    MultiItemsDisplayer,
)
from .define import MachineRecipeRendererBase


class _ToolDisplayer(MultiItemsDisplayer):
    def __init__(self, ctrl, items, tool_name, level_name):
        self.tool_name = tool_name
        self.level_name = level_name
        MultiItemsDisplayer.__init__(self, ctrl, items)

    def onBtnReleased(self, params):
        item = self.get_current_carousel_item()
        text = CF.CreateItem(LEVEL_ID).GetItemFormattedHoverText(item.id) or item.id
        text += "\n§e不被消耗。\n§7最低%s等级： §f%s" % (
            self.tool_name, self.level_name,
        )
        x, y = self.ctrl.GetRootPos()
        width, height = self.ctrl.GetSize()
        CreateDescBoard(
            self.ctrl, (x + width, y - height), CategoryType.ITEM,
            item.id, item.id, text,
        )


class MachineryWorkstationRecipeRenderer(MachineRecipeRendererBase):
    recipe_icon_id = machinery.Machinery.MACHINERY_WORKSTATION
    render_ui_def_name = "RecipeCheckerLib.machinery_workstation_recipes"

    LEVEL_IRON = 1
    LEVEL_INVAR = 2
    LEVEL_MAPPING = {
        LEVEL_IRON: "铁",
        LEVEL_INVAR: "殷钢",
    }

    def __init__(self, recipe):
        # type: (MachineryWorkstationRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self.dyn_item_renderers = []  # type: list[InputDisplayer | MultiItemsDisplayer]
        content = panel["content"]
        input_items = self.recipe.inputs.get("item", {})
        for slot, input in input_items.items():
            displayer = InputDisplayer(content["input/%d" % slot], input)
            if input.count not in (0, 1):
                displayer.item_count_label.SetText(str(int(input.count)))
            self.dyn_item_renderers.append(displayer)
        if self.recipe.wrench_level > 0:
            self.dyn_item_renderers.append(
                _ToolDisplayer(
                    content["side/0"],
                    get_spec_level_avail_wrenchs(self.recipe.wrench_level),
                    "扳手", self.LEVEL_MAPPING.get(self.recipe.wrench_level, str(self.recipe.wrench_level)),
                )
            )
        if self.recipe.pincer_level > 0:
            self.dyn_item_renderers.append(
                _ToolDisplayer(
                    content["side/1"],
                    get_spec_level_avail_pincers(self.recipe.pincer_level),
                    "钳", self.LEVEL_MAPPING.get(self.recipe.pincer_level, str(self.recipe.pincer_level)),
                )
            )
        ItemDisplayer(content["output/0"], Item(self.recipe.output_item_id))

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        for input_render in self.dyn_item_renderers:
            input_render.tick(render_ticks)


MachineryWorkstationRecipe.SetRenderer(MachineryWorkstationRecipeRenderer)
