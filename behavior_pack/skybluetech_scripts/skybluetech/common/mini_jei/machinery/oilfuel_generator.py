# coding=utf-8
from ...define.id_enum import Machinery
from ..core import CategoryType, Input
from .define import GeneratorRecipe


class OilFuelGeneratorRecipe(GeneratorRecipe):
    recipe_icon_id = Machinery.OILFUEL_GENERATOR

    def __init__(
        self,
        input_fluid_id,  # type: str
        input_fluid_volume,  # type: float
        output_power,  # type: int
        tick_duration,  # type: int
    ):
        GeneratorRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid_id, input_fluid_volume)}},
            output_power,
            tick_duration,
        )

    def Marshal(self):
        fuel = self.inputs[CategoryType.FLUID][0]
        return {
            "input_fluid_id": fuel.id,
            "input_fluid_volume": fuel.count,
            "output_power": self.output_power,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid_id=data["input_fluid_id"],
            input_fluid_volume=data["input_fluid_volume"],
            output_power=data["output_power"],
            tick_duration=data["tick_duration"],
        )
