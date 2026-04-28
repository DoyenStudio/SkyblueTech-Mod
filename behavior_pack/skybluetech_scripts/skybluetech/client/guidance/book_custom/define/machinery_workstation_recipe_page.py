# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.richer_text import (
    RicherTextCtrl,
    RicherTextOpt,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe,
)
from skybluetech_scripts.skybluetech.common.mini_jei import (
    GetRecipesByOutput,
    CategoryType,
)
from .base_page import BasePage


class MachineryWorkstationRecipePage(BasePage):
    ctrl_def_name = "GuidanceLib.machinery_workstation_render_page"

    def __init__(self, recipe_result, extra_text=None):
        # type: (str, str | None) -> None
        BasePage.__init__(self)
        self.recipe_result = recipe_result
        self.extra_text = extra_text
        self.dyn_recipe_renderer = None

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        from ....ui.recipe_checker import PushRecipeCheckerUI

        BasePage.RenderInit(self, ctrl)
        recipes = GetRecipesByOutput(CategoryType.ITEM, self.recipe_result)
        for recipe in recipes:
            if isinstance(recipe, MachineryWorkstationRecipe):
                self.dyn_recipe_renderer = recipe.GetRendererForced()(recipe)
                self.dyn_recipe_renderer.RenderInit(ctrl["recipe_renderer"])
                ctrl["check_btn"].asButton().SetCallback(
                    lambda _: PushRecipeCheckerUI(recipes) and None
                )
                break
        else:
            title = ctrl["title"].asLabel()
            title.SetText("§c错误： 未找到关于 %s 的配方。" % self.recipe_result)
            title.base.SetTextFontSize(1)
        if self.extra_text is not None:
            RicherTextCtrl(ctrl["text_content"]).SetText(self.extra_text)

    def DeRender(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.DeRender(self, ctrl)
        if self.dyn_recipe_renderer is not None:
            self.dyn_recipe_renderer.DeRender(ctrl["recipe_renderer"])
