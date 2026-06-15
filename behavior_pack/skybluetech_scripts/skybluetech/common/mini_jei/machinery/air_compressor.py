# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Output


class AirCompressorRecipe(MachineRecipe):
    recipe_icon_id = machinery.AIR_COMPRESSOR

    def __init__(
        self, dimension, output_fluid_id, output_fluid_volume, power_cost, tick_duration
    ):
        # type: (int, str, float, int, int) -> None
        MachineRecipe.__init__(
            self,
            {},
            {CategoryType.FLUID: {0: Output(output_fluid_id, output_fluid_volume)}},
            power_cost,
            tick_duration,
        )
        self.dimension = dimension
        self.output_fluid_id = output_fluid_id
        self.output_fluid_volume = output_fluid_volume

    def equals(self, other):
        return (
            MachineRecipe.equals(self, other)
            and getattr(other, "dimension", None) == self.dimension
        )

    def Marshal(self):
        return {
            "dimension": self.dimension,
            "output_fluid_id": self.output_fluid_id,
            "output_fluid_volume": self.output_fluid_volume,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            dimension=data.get("dimension", 0),
            output_fluid_id=data["output_fluid_id"],
            output_fluid_volume=data["output_fluid_volume"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
