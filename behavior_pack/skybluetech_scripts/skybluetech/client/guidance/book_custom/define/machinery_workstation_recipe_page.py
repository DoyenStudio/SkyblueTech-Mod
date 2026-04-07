# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.mini_jei import (
    GetRecipesByOutput,
    CategoryType,
)
from .base_page import BasePage


class MachineryWorkstationRecipePage(BasePage):
    ctrl_def_name = "GuidanceLib.machinery_workstation_render_page"

    def __init__(self, page_id, recipe_result):
        # type: (str, str) -> None
        BasePage.__init__(self, page_id)
        self.recipe_result = recipe_result

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        recipes = GetRecipesByOutput(CategoryType.ITEM, self.recipe_result)
        if len(recipes) > 0:
            recipe = recipes[0]
            recipe.RenderInit(ctrl["recipe_renderer"])
        else:
            title = ctrl["title"].asLabel()
            title.SetText("§c错误： 未找到关于 %s 的配方。" % self.recipe_result)
            title.base.SetTextFontSize(1)
