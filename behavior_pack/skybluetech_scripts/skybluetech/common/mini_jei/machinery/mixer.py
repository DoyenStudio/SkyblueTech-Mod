# coding=utf-8
#
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output

TAG_DUST_BLOCK = "dust_block"


class MixerRecipe(MachineRecipe):
    recipe_icon_id = machinery.MIXER
    render_ui_def_name = "RecipeCheckerLib.mixer_recipes"

    def __init__(
        self,
        input_fluid_id,  # type: str
        input_volume,  # type: float
        input_item_id,  # type: str
        input_count,  # type: int
        output_item_id,  # type: str
        output_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {
                CategoryType.FLUID: {0: Input(input_fluid_id, input_volume)},
                CategoryType.ITEM: {0: Input(input_item_id, input_count)},
            },
            {CategoryType.ITEM: {1: Output(output_item_id, output_count)}},
            power_cost,
            tick_duration,
        )
        self.input_fluid_id = input_fluid_id
        self.input_volume = input_volume
        self.input_item_id = input_item_id
        self.input_count = input_count
        self.output_item_id = output_item_id
        self.output_count = output_count

    def Marshal(self):
        return {
            "input_fluid_id": self.input_fluid_id,
            "input_volume": self.input_volume,
            "input_item_id": self.input_item_id,
            "input_count": self.input_count,
            "output_item_id": self.output_item_id,
            "output_count": self.output_count,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid_id=data["input_fluid_id"],
            input_volume=data["input_volume"],
            input_item_id=data["input_item_id"],
            input_count=data["input_count"],
            output_item_id=data["output_item_id"],
            output_count=data["output_count"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
