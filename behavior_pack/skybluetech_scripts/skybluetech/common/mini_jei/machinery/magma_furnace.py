# coding=utf-8
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


def sec(second):
    # type: (float) -> int
    return int(second * 20)


class MagmaFurnaceRecipe(MachineRecipe):
    recipe_icon_id = machinery.MAGMA_FURNACE
    render_ui_def_name = "RecipeCheckerLib.magma_furnace_recipes"

    def __init__(
        self,
        input_item_id,
        is_tag,
        output_fluid_id,
        output_volume,
        power_cost,
        tick_duration,
    ):
        # type: (str, bool, str, float, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_item_id, is_tag=is_tag)}},
            {CategoryType.FLUID: {0: Output(output_fluid_id, output_volume)}},
            power_cost,
            tick_duration,
        )
        self.input_item_id = input_item_id
        self.is_tag = is_tag
        self.output_fluid_id = output_fluid_id
        self.output_volume = output_volume

    def Marshal(self):
        # type: () -> dict
        return {
            "input_item_id": self.input_item_id,
            "is_tag": self.is_tag,
            "output_fluid_id": self.output_fluid_id,
            "output_volume": self.output_volume,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_item_id=data["input_item_id"],
            is_tag=data["is_tag"],
            output_fluid_id=data["output_fluid_id"],
            output_volume=data["output_volume"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
