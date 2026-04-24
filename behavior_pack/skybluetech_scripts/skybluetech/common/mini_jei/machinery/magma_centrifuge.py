# coding=utf-8
#
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class MagmaCentrifugeRecipe(MachineRecipe):
    recipe_icon_id = machinery.MAGMA_CENTRIFUGE
    render_ui_def_name = "RecipeCheckerLib.magma_centrifuge_recipes"

    def __init__(
        self, input_fluid, input_volume, output_fluids, power_cost, tick_duration
    ):
        # type: (str, float, dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: output_fluids},
            power_cost,
            tick_duration,
        )
        self.input_fluid = input_fluid
        self.input_volume = input_volume
        self.output_fluids = output_fluids

    def Marshal(self):
        return {
            "input_fluid": self.input_fluid,
            "input_volume": self.input_volume,
            "output_fluids": self.output_fluids,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_fluids=data["output_fluids"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
