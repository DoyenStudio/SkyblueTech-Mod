# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe,
    get_spec_level_avail_wrenchs,
    get_spec_level_avail_pincers,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import (
    InputDisplayer,
    MultiItemsDisplayer,
)
from .define import MachineRecipeRendererBase


class MachineryWorkstationRecipeRenderer(MachineRecipeRendererBase):
    recipe_icon_id = machinery.MACHINERY_WORKSTATION
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
        input_items = self.recipe.inputs.get("item", {})
        for slot, input in input_items.items():
            self.dyn_item_renderers.append(
                InputDisplayer(panel["slot%d" % slot], input)
            )
        if self.recipe.wrench_level > 0:
            self.dyn_item_renderers.append(
                MultiItemsDisplayer(
                    panel["wrench_slot"],
                    get_spec_level_avail_wrenchs(self.recipe.wrench_level),
                )
            )
        if self.recipe.pincer_level > 0:
            self.dyn_item_renderers.append(
                MultiItemsDisplayer(
                    panel["pincer_slot"],
                    get_spec_level_avail_pincers(self.recipe.pincer_level),
                )
            )
        ItemDisplayer(panel["output_slot"], Item(self.recipe.output_item_id))
        panel["level_tip"].asLabel().SetText(
            "扳手等级： %s\n钳等级： %s"
            % (
                self.LEVEL_MAPPING[self.recipe.wrench_level],
                self.LEVEL_MAPPING[self.recipe.pincer_level],
            )
        )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        for input_render in self.dyn_item_renderers:
            input_render.tick(render_ticks)


MachineryWorkstationRecipe.SetRenderer(MachineryWorkstationRecipeRenderer)
