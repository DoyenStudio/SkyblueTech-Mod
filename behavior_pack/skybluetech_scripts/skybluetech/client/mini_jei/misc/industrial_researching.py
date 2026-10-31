# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import INSCRIBING_TEMPLATE
from skybluetech_scripts.skybluetech.common.mini_jei.misc.industrial_researching import (
    IndustrialResearchingRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import InputDisplayer
from ..core import RecipeRenderer


class IndustrialResearchingRecipeRenderer(RecipeRenderer):
    recipe_icon_id = INSCRIBING_TEMPLATE
    render_ui_def_name = "RecipeCheckerLib.industrial_researching_recipes"
    minijei_title = "机件加工台： 工业研究"

    def __init__(self, recipe):
        # type: (IndustrialResearchingRecipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.input_renderers = []

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        self.input_renderers = []
        content = panel_ctrl["content"]
        require_items = self.recipe.require_items[:9]
        for index in range(9):
            slot_ctrl = content["input/%d" % index]
            if index >= len(require_items):
                slot_ctrl.SetVisible(False)
                continue
            slot_ctrl.SetVisible(True)
            input_renderer = InputDisplayer(slot_ctrl, require_items[index])
            count = require_items[index].count
            if count not in (0, 1):
                input_renderer.item_count_label.SetText(str(int(count)))
            self.input_renderers.append(input_renderer)

        self.template_renderer = ItemDisplayer(
            content["output/1"], Item(INSCRIBING_TEMPLATE)
        )
        self.result_renderer = ItemDisplayer(
            content["output/0"], Item(self.recipe.result_item_id)
        )
        content["xp_cost_label"].asLabel().SetText(
            "花费经验 Lv %s" % self.recipe.require_exp_level
        )

    def RenderUpdate(self, panel_ctrl, render_ticks):
        # type: (UBaseCtrl, int) -> None
        for input_renderer in self.input_renderers:
            input_renderer.tick(render_ticks)


IndustrialResearchingRecipe.SetRenderer(IndustrialResearchingRecipeRenderer)
