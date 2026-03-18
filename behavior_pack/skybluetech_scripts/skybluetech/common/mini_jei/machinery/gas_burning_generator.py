# coding=utf-8
from ....common.define.id_enum import machinery
from ..core import CategoryType, Input, Output
from .recipe_cls import GeneratorRecipe


class GasBurningGeneratorRecipe(GeneratorRecipe):
    recipe_icon_id = machinery.GAS_BURNING_GENERATOR
    render_ui_def_name = "RecipeCheckerLib.gas_burning_generator_recipes"

    def __init__(
        self,
        gas_id,  # type: str
        once_burning_volume,  # type: float
        output_power,  # type: int
        output_gas_id=None,  # type: str | None
        output_gas_volume=0,  # type: float
    ):
        outputs = (
            {CategoryType.FLUID: {1: Output(output_gas_id, output_gas_volume)}}
            if output_gas_id is not None
            else None
        )
        GeneratorRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(gas_id, once_burning_volume)}},
            output_power,
            1,
            outputs,
        )
        self.gas_id = gas_id
        self.once_burning_volume = once_burning_volume
        self.output_power = output_power
        self.output_gas_id = output_gas_id
        self.output_gas_volume = output_gas_volume
