# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ..core import UnmarshalOrderedOutputs
from .define import CategoryType, MachineRecipe, Input, Output


class MagmaCentrifugeRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.MAGMA_CENTRIFUGE

    def __init__(
        self, input_fluid, input_volume, output_fluids, power_cost, tick_duration,
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
        result = {
            "input_fluid": self.input_fluid,
            "input_volume": self.input_volume,
            "output_fluids": {
                str(slot): output.to_dict()
                for slot, output in self.output_fluids.items()
            },
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_fluids=UnmarshalOrderedOutputs(
                {CategoryType.FLUID: data["output_fluids"]}
            )[CategoryType.FLUID],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
