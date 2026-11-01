# coding=utf-8
from ...define.id_enum import RF
from ..core import (
    Recipe,
    Input,
    Output,
    CategoryType,
    RecipesCollection,
)


class MachineRecipeBase(Recipe):
    def __init__(
        self,
        inputs=None,  # type: dict[str, dict[int, Input]] | None
        outputs=None,  # type: dict[str, dict[int, Output]] | None
        tick_duration=1,  # type: int
        inputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Input]]] | None
        outputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Output]]] | None
    ):
        Recipe.__init__(self, inputs, outputs, inputs_unordered, outputs_unordered)
        self.tick_duration = tick_duration

    def GetMachineInputs(self):
        return self.inputs

    def GetMachineOutputs(self):
        return self.outputs

    def GetMachineUnorderedInputs(self):
        # type: () -> dict[str, dict[tuple[int, ...], list[Input]]] | None
        return self.inputs_unordered

    def GetMachineUnorderedOutputs(self):
        # type: () -> dict[str, dict[tuple[int, ...], list[Output]]] | None
        return self.outputs_unordered

    def GetTickDuration(self):
        return self.tick_duration

    def Marshal(self):
        result = Recipe.Marshal(self)
        result["tick_duration"] = self.tick_duration
        return result

    @classmethod
    def Unmarshal(cls, dct):
        recipe = Recipe.Unmarshal(dct)
        return cls(
            inputs=recipe.inputs,
            outputs=recipe.outputs,
            tick_duration=dct["tick_duration"],
            inputs_unordered=recipe.inputs_unordered,
            outputs_unordered=recipe.outputs_unordered,
        )


class MachineRecipe(MachineRecipeBase):
    def __init__(
        self,
        inputs=None,  # type: dict[str, dict[int, Input]] | None
        outputs=None,  # type: dict[str, dict[int, Output]] | None
        power_cost=1,  # type: int
        tick_duration=1,  # type: int
        inputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Input]]] | None
        outputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Output]]] | None
    ):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int, int, dict[str, dict[tuple[int, ...], list[Input]]] | None, dict[str, dict[tuple[int, ...], list[Output]]] | None) -> None
        MachineRecipeBase.__init__(
            self, inputs, outputs, tick_duration, inputs_unordered, outputs_unordered
        )
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def Marshal(self):
        result = MachineRecipeBase.Marshal(self)
        result["power_cost"] = self.power_cost
        return result

    @classmethod
    def Unmarshal(
        cls,
        dct,  # type: dict
    ):
        recipe = Recipe.Unmarshal(dct)
        return cls(
            inputs=recipe.inputs,
            outputs=recipe.outputs,
            power_cost=dct["power_cost"],
            tick_duration=dct["tick_duration"],
            inputs_unordered=recipe.inputs_unordered,
            outputs_unordered=recipe.outputs_unordered,
        )

    def __repr__(self):
        return (
            "MachineRecipe(%s, %s, %d, %d, inputs_unordered=%s, outputs_unordered=%s)"
            % (
                self.inputs,
                self.outputs,
                self.power_cost,
                self.tick_duration,
                self.inputs_unordered,
                self.outputs_unordered,
            )
        )

    def __hash__(self):
        return hash((tuple(self.inputs or {}), tuple(self.outputs or {})))


class GeneratorRecipe(MachineRecipeBase):
    def __init__(
        self,
        inputs=None,  # type: dict[str, dict[int, Input]] | None
        output_power=0,  # type: int
        tick_duration=1,  # type: int
        outputs=None,  # type: dict[str, dict[int, Output]] | None
        inputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Input]]] | None
        outputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Output]]] | None
    ):
        _outputs = {CategoryType.ENERGY: {0: Output(RF, output_power)}}
        if outputs is not None:
            _outputs.update(outputs)
        MachineRecipeBase.__init__(
            self, inputs, _outputs, tick_duration, inputs_unordered, outputs_unordered
        )
        self.output_power = output_power

    def Marshal(self):
        result = MachineRecipeBase.Marshal(self)
        result["output_power"] = self.output_power
        return result

    @classmethod
    def Unmarshal(
        cls,
        dct,  # type: dict
    ):
        recipe = Recipe.Unmarshal(dct)
        return cls(
            inputs=recipe.inputs,
            output_power=dct["output_power"],
            tick_duration=dct["tick_duration"],
            outputs=recipe.outputs,
            inputs_unordered=recipe.inputs_unordered,
            outputs_unordered=recipe.outputs_unordered,
        )

    def __repr__(self):
        return (
            "GeneratorRecipe(%s, %s, %d, %d, inputs_unordered=%s, outputs_unordered=%s)"
            % (
                self.inputs,
                self.outputs,
                self.output_power,
                self.tick_duration,
                self.inputs_unordered,
                self.outputs_unordered,
            )
        )

    def __hash__(self):
        return hash(
            (tuple(self.inputs or {}), tuple(self.outputs or {}), self.tick_duration)
        )


__all__ = [
    "CategoryType",
    "GeneratorRecipe",
    "Input",
    "MachineRecipe",
    "MachineRecipeBase",
    "Output",
    "RecipesCollection",
]
