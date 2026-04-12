# coding=utf-8
from ....common.define.id_enum import machinery
from ..core import CategoryType, Input, Output
from .define import GeneratorRecipe

if 0:
    from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl


class RedstoneGeneratorRecipe(GeneratorRecipe):
    recipe_icon_id = machinery.REDSTONE_GENERATOR
    render_ui_def_name = "RecipeCheckerLib.redstone_generator_recipes"

    def __init__(
        self,
        item_id,  # type: str
        output_item_id,  # type: str
        output_item_count,  # type: int
        output_power,  # type: int
        tick_duration,  # type: int
    ):
        GeneratorRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(item_id)}},
            output_power,
            tick_duration,
            outputs={CategoryType.ITEM: {1: Output(output_item_id, output_item_count)}},
        )
        self.input_item_id = item_id
