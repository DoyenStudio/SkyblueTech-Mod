# coding=utf-8
from ..core import CategoryType, RecipeBase, RegisterRecipe


class Element(object):
    def __init__(self, id, count=1):
        # type: (str, float) -> None
        self.id = id
        self.count = count

    def __repr__(self):
        return "io(%s, %d)" % (self.id, self.count)


class Input(Element):
    def __init__(self, id, count=1, is_tag=False):
        # type: (str, float, bool) -> None
        Element.__init__(self, id, count)
        self.is_tag = is_tag


class Output(Element):
    pass


class Recipe(RecipeBase):
    def __init__(self, inputs, outputs):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]]) -> None
        self.inputs = inputs
        "配方输入: [配方类型: [槽位: 输入元素]]"
        self.outputs = outputs
        "配方输出: [配方类型: [槽位: 输出元素]]"
        RegisterRecipe(self)

    def equals(self, other):
        # type: (Recipe | None) -> bool
        if other is None:
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs

    def GetInputs(self):
        return {
            cat: [
                ("tag:" + input.id if input.is_tag else input.id)
                for input in slot2input.values()
            ]
            for cat, slot2input in self.inputs.items()
        }

    def GetOutputs(self):
        return {
            cat: [output.id for output in slot2output.values()]
            for cat, slot2output in self.outputs.items()
        }


class MachineRecipe(Recipe):
    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int, int) -> None
        Recipe.__init__(self, inputs, outputs)
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def __repr__(self):
        return "MachineRecipe(%s, %s, %d, %d)" % (
            self.inputs,
            self.outputs,
            self.power_cost,
            self.tick_duration,
        )

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.outputs)))




# class PresetMachineRecipe(object):
#     def __init__(self, icon_id, power_cost, tick_duration):
#         # type: (str, int, int) -> None
#         self.icon_id = icon_id
#         self.power_cost = power_cost
#         self.tick_duration = tick_duration

#     def Simple11Recipe(self, input_id, output_id):
#         # type: (str, str) -> MachineRecipe
#         return MachineRecipe(
#             self.icon_id,
#             {"item": {0: Input(input_id, 1)}},
#             {"item": {1: Output(output_id, 1)}},
#             self.power_cost,
#             self.tick_duration,
#         )

#     def SimpleXXRecipe(self, input_id, input_count, output_id, output_count):
#         # type: (str, int, str, int) -> MachineRecipe
#         return MachineRecipe(
#             self.icon_id,
#             {"item": {0: Input(input_id, input_count)}},
#             {"item": {1: Output(output_id, output_count)}},
#             self.power_cost,
#             self.tick_duration,
#         )

#     def Simple11TagRecipe(self, input_tag, output_id):
#         # type: (str, str) -> MachineRecipe
#         return MachineRecipe(
#             self.icon_id,
#             {"item": {0: Input(input_tag, 1, is_tag=True)}},
#             {"item": {1: Output(output_id, 1)}},
#             self.power_cost,
#             self.tick_duration,
#         )

#     def SimpleXXTagRecipe(self, input_tag, input_count, output_id, output_count):
#         # type: (str, int, str, int) -> MachineRecipe
#         return MachineRecipe(
#             self.icon_id,
#             {"item": {0: Input(input_tag, input_count, is_tag=True)}},
#             {"item": {1: Output(output_id, output_count)}},
#             self.power_cost,
#             self.tick_duration,
#         )

#     def Recipe(self, inputs, outputs):
#         # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]]) -> MachineRecipe
#         return MachineRecipe(self.icon_id, inputs, outputs, self.power_cost, self.tick_duration)

#     def ItemRecipe(self, inputs, outputs):
#         # type: (dict[int, Input], dict[int, Output]) -> MachineRecipe
#         return MachineRecipe(
#             self.icon_id,
#             {"item": inputs},
#             {"item": outputs},
#             self.power_cost,
#             self.tick_duration
#         )
