# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    machinery,
    INSCRIBING_TEMPLATE,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.template_assembler import (
    TemplateAssemblerRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from .define import MachineRecipeRenderer


class TemplateAssemblerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = machinery.Machinery.TEMPLATE_ASSEMBLER
    render_ui_def_name = "RecipeCheckerLib.template_assembler_recipes"

    def __init__(self, recipe):
        # type: (TemplateAssemblerRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRenderer.RenderInit(self, panel)
        ItemDisplayer(panel["slot9"], Item(INSCRIBING_TEMPLATE))


TemplateAssemblerRecipe.SetRenderer(TemplateAssemblerRecipeRenderer)
