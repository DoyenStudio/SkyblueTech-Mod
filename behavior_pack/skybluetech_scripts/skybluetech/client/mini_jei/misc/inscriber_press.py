# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.common.misc.inscriber_press import EMPTY
from skybluetech_scripts.skybluetech.common.mini_jei.misc.inscriber_press import InscriberPressRecipe
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import InputDisplayer
from ..core import RecipeRenderer
from skybluetech_scripts.skybluetech.common.mini_jei.core import CategoryType


class InscriberPressRecipeRenderer(RecipeRenderer):
    recipe_icon_id = EMPTY
    render_ui_def_name = "InscriberPressRecipe.row"
    minijei_title = "压印模板雕刻"

    def RenderInit(self, panel_ctrl):
        content = panel_ctrl["content"]
        self.input_renderer = InputDisplayer(
            content["input/0"], self.recipe.inputs[CategoryType.ITEM][0])
        self.output_renderer = ItemDisplayer(
            content["output/0"], Item(self.recipe.output_id))
        for index, value in enumerate(self.recipe.grid):
            cell = content["pattern/cell_%d" % index]
            color = (1, 1, 1) if value else (0, 0, 0)
            cell["base"].asImage().SetSpriteColor(color)
            pulse = cell["pulse"]
            pulse.SetVisible(not value)
            if not value:
                pulse.base.PlayAnimation()
            else:
                pulse.base.StopAnimation()

    def RenderUpdate(self, panel_ctrl, render_ticks):
        self.input_renderer.tick(render_ticks)


InscriberPressRecipe.SetRenderer(InscriberPressRecipeRenderer)
