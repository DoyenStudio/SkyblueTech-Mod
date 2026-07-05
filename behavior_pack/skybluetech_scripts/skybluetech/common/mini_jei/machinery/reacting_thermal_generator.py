# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ..core import CategoryType, Input, Output
from .define import GeneratorRecipe


class ReactingThermalGeneratorRecipe(GeneratorRecipe):
    recipe_icon_id = machinery.Machinery.REACTING_THERMAL_GENERATOR

    def __init__(
        self,
        input_item_id,  # type: str
        input_fluid_id,  # type: str
        input_fluid_volume,  # type: float
        output_fluid_id,  # type: str
        output_fluid_volume,  # type: float
        output_power,  # type: int
        tick_duration,  # type: int
    ):
        GeneratorRecipe.__init__(
            self,
            {
                CategoryType.ITEM: {0: Input(input_item_id)},
                CategoryType.FLUID: {0: Input(input_fluid_id, input_fluid_volume)},
            },
            output_power,
            tick_duration,
            outputs={
                CategoryType.FLUID: {1: Output(output_fluid_id, output_fluid_volume)}
            },
        )
        self.input_item_id = input_item_id
        self.input_fluid_id = input_fluid_id
        self.input_fluid_volume = input_fluid_volume
        self.output_fluid_id = output_fluid_id
        self.output_fluid_volume = output_fluid_volume

    def Marshal(self):
        return {
            "input_item_id": self.input_item_id,
            "input_fluid_id": self.input_fluid_id,
            "input_fluid_volume": self.input_fluid_volume,
            "output_fluid_id": self.output_fluid_id,
            "output_fluid_volume": self.output_fluid_volume,
            "output_power": self.output_power,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_item_id=data["input_item_id"],
            input_fluid_id=data["input_fluid_id"],
            input_fluid_volume=data["input_fluid_volume"],
            output_fluid_id=data["output_fluid_id"],
            output_fluid_volume=data["output_fluid_volume"],
            output_power=data["output_power"],
            tick_duration=data["tick_duration"],
        )
