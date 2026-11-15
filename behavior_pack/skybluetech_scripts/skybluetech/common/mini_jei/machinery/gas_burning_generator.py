# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ..core import CategoryType, Input, Output
from .define import GeneratorRecipe


class GasBurningGeneratorRecipe(GeneratorRecipe):
    recipe_icon_id = machinery.Machinery.GAS_BURNING_GENERATOR

    def __init__(
        self,
        gas_id,  # type: str
        once_burning_volume,  # type: float
        output_power,  # type: int
        output_gas_id=None,  # type: str | None
        output_gas_volume=0,  # type: float
        second_gas_id=None,  # type: str | None
        second_burning_volume=0,  # type: float
    ):
        inputs = {CategoryType.FLUID: {0: Input(gas_id, once_burning_volume)}}
        if second_gas_id is not None:
            if second_burning_volume <= 0:
                raise ValueError("second_burning_volume must be positive")
            inputs[CategoryType.FLUID][2] = Input(second_gas_id, second_burning_volume)
        elif second_burning_volume != 0:
            raise ValueError("second_gas_id is required for a second input")
        outputs = (
            {CategoryType.FLUID: {1: Output(output_gas_id, output_gas_volume)}}
            if output_gas_id is not None
            else None
        )
        GeneratorRecipe.__init__(
            self,
            inputs,
            output_power,
            1,
            outputs,
        )
        self.gas_id = gas_id
        self.once_burning_volume = once_burning_volume
        self.output_power = output_power
        self.output_gas_id = output_gas_id
        self.output_gas_volume = output_gas_volume
        self.second_gas_id = second_gas_id
        self.second_burning_volume = second_burning_volume

    def Marshal(self):
        # type: () -> dict
        result = {
            "gas_id": self.gas_id,
            "once_burning_volume": self.once_burning_volume,
            "output_power": self.output_power,
            "output_gas_id": self.output_gas_id,
            "output_gas_volume": self.output_gas_volume,
            "second_gas_id": self.second_gas_id,
            "second_burning_volume": self.second_burning_volume,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> GasBurningGeneratorRecipe
        return cls(
            gas_id=data["gas_id"],
            once_burning_volume=data["once_burning_volume"],
            output_power=data["output_power"],
            output_gas_id=data["output_gas_id"],
            output_gas_volume=data["output_gas_volume"],
            second_gas_id=data.get("second_gas_id"),
            second_burning_volume=data.get("second_burning_volume", 0),
        )
