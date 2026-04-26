# coding=utf-8
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class OilExtractorRecipe(MachineRecipe):
    recipe_icon_id = machinery.OIL_EXTRACTOR
    render_ui_def_name = "RecipeCheckerLib.oil_extractor_recipes"

    def __init__(
        self,
        input_item_id,  # type: str
        output_fluid_id,  # type: str
        output_fluid_volume,  # type: float
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_item_id, 1)}},
            {CategoryType.FLUID: {0: Output(output_fluid_id, output_fluid_volume)}},
            power_cost,
            tick_duration,
        )
        self.input_item_id = input_item_id
        self.output_fluid_id = output_fluid_id
        self.output_fluid_volume = output_fluid_volume

    def Marshal(self):
        return {
            "input_item_id": self.input_item_id,
            "output_fluid_id": self.output_fluid_id,
            "output_fluid_volume": self.output_fluid_volume,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_item_id=data["input_item_id"],
            output_fluid_id=data["output_fluid_id"],
            output_fluid_volume=data["output_fluid_volume"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
