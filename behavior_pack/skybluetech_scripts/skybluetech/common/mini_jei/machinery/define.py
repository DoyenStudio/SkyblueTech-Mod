# coding=utf-8
from ...define.id_enum import RF
from ..core import (
    Recipe,
    Input,
    Output,
    CategoryType,
    RecipesCollection,
    MarshalInputs,
    MarshalOutputs,
    UnmarshalInputs,
    UnmarshalOutputs,
)


class MachineRecipeBase(Recipe):
    def __init__(self, inputs, outputs, tick_duration):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int) -> None
        Recipe.__init__(self, inputs, outputs)
        self.tick_duration = tick_duration


class MachineRecipe(MachineRecipeBase):
    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int, int) -> None
        MachineRecipeBase.__init__(self, inputs, outputs, tick_duration)
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def Marshal(self):
        return {
            "inputs": MarshalInputs(self.inputs),
            "outputs": MarshalOutputs(self.outputs),
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(
        cls,
        dct,  # type: dict
    ):
        return cls(
            inputs=UnmarshalInputs(dct["inputs"]),
            outputs=UnmarshalOutputs(dct["outputs"]),
            power_cost=dct["power_cost"],
            tick_duration=dct["tick_duration"],
        )

    def __repr__(self):
        return "MachineRecipe(%s, %s, %d, %d)" % (
            self.inputs,
            self.outputs,
            self.power_cost,
            self.tick_duration,
        )

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.outputs)))


class GeneratorRecipe(MachineRecipeBase):
    def __init__(self, inputs, output_power, tick_duration, outputs=None):
        # type: (dict[str, dict[int, Input]], int, int, dict[str, dict[int, Output]] | None) -> None
        _outputs = {CategoryType.ENERGY: {0: Output(RF, output_power)}}
        if outputs is not None:
            _outputs.update(outputs)
        MachineRecipeBase.__init__(self, inputs, _outputs, tick_duration)
        self.output_power = output_power

    def Marshal(self):
        return {
            "inputs": MarshalInputs(self.inputs),
            "outputs": MarshalOutputs(self.outputs),
            "output_power": self.output_power,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(
        cls,
        dct,  # type: dict
    ):
        return cls(
            inputs=UnmarshalInputs(dct["inputs"]),
            output_power=dct["output_power"],
            tick_duration=dct["tick_duration"],
            outputs=UnmarshalOutputs(dct["outputs"]),
        )

    def __repr__(self):
        return "GeneratorRecipe(%s, %s, %d, %d)" % (
            self.inputs,
            self.outputs,
            self.output_power,
            self.tick_duration,
        )

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.outputs), self.tick_duration))


__all__ = [
    "CategoryType",
    "Input",
    "Output",
    "MachineRecipe",
    "MachineRecipeBase",
    "RecipesCollection",
    "GeneratorRecipe",
]
