# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.machinery_def.precision_cutter import (
    CUTTER_LEVEL_MAPPING,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.precision_cutter import (
    PrecisionCutterRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from .define import MachineRecipeRenderer


def GetCutterIdForLevel(required_level):
    # type: (int) -> str | None
    "从 common 端 cutter 表中挑选满足等级要求的最低级锯片。"
    best = None  # type: str | None
    best_level = None  # type: int | None
    for cutter_id, level in CUTTER_LEVEL_MAPPING.items():
        if level < required_level:
            continue
        if best_level is None or level < best_level:
            best = cutter_id
            best_level = level
    return best


class PrecisionCutterRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = machinery.Machinery.PRECISION_CUTTER
    render_ui_def_name = "RecipeCheckerLib.precision_cutter_recipes"

    def __init__(self, recipe):
        # type: (PrecisionCutterRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRenderer.RenderInit(self, panel)
        cutter_id = GetCutterIdForLevel(self.recipe.cutter_level)
        if cutter_id is not None:
            ItemDisplayer(panel["cutter_slot"], Item(cutter_id))


PrecisionCutterRecipe.SetRenderer(PrecisionCutterRecipeRenderer)
