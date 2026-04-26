# coding=utf-8
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output

MC_METAL = {"copper", "iron", "gold"}


class FluidCondenserRecipe(MachineRecipe):
    recipe_icon_id = machinery.FLUID_CONDENSER
    render_ui_def_name = "RecipeCheckerLib.fluid_condenser_recipes"

    def __init__(
        self,
        input_fluid,  # type: str
        input_fluid_volume,  # type: float
        output_item,  # type: str
        output_item_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_fluid_volume)}},
            {CategoryType.ITEM: {0: Output(output_item, output_item_count)}},
            power_cost,
            tick_duration,
        )
        self.input_fluid = input_fluid
        self.input_fluid_volume = input_fluid_volume
        self.output_item = output_item
        self.output_item_count = output_item_count

    def Marshal(self):
        return {
            "input_fluid": self.input_fluid,
            "input_fluid_volume": self.input_fluid_volume,
            "output_item": self.output_item,
            "output_item_count": self.output_item_count,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid=data["input_fluid"],
            input_fluid_volume=data["input_fluid_volume"],
            output_item=data["output_item"],
            output_item_count=data["output_item_count"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )


def recipe_molten2ingot(metal_id, power_cost=80, tick_duration=180):
    # type: (str, int, int) -> FluidCondenserRecipe
    return FluidCondenserRecipe(
        "skybluetech:molten_" + metal_id,
        144,
        ("minecraft:" if metal_id in MC_METAL else "skybluetech:")
        + metal_id
        + "_ingot",
        1,
        power_cost,
        tick_duration,
    )
