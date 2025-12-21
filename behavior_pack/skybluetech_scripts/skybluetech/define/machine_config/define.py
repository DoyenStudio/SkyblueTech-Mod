# coding=utf-8
#

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


class Recipe(object):
    def __init__(self, inputs, outputs):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]]) -> None
        self.inputs = inputs
        "配方输入: [配方类型: [槽位: 输入元素]]"
        self.outputs = outputs
        "配方输出: [配方类型: [槽位: 输出元素]]"

    def equals(self, other):
        # type: (Recipe | None) -> bool
        if other is None:
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs


class MachineRecipe(Recipe):
    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]], int, int) -> None
        Recipe.__init__(self, inputs, outputs)
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def __repr__(self):
        return "MachineRecipe(%s, %s, %d, %d)" % (self.inputs, self.outputs, self.power_cost, self.tick_duration)

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.outputs)))


class PresetMachineRecipe(object):
    def __init__(self, power_cost, tick_duration):
        # type: (int, int) -> None
        self.power_cost = power_cost
        self.tick_duration = tick_duration

    def Simple11Recipe(self, input_id, output_id):
        # type: (str, str) -> MachineRecipe
        return MachineRecipe({"item": {0: Input(input_id, 1)}}, {"item": {1: Output(output_id, 1)}}, self.power_cost, self.tick_duration)

    def SimpleXXRecipe(self, input_id, input_count, output_id, output_count):
        # type: (str, int, str, int) -> MachineRecipe
        return MachineRecipe({"item": {0: Input(input_id, input_count)}}, {"item": {1: Output(output_id, output_count)}}, self.power_cost, self.tick_duration)

    def Simple11TagRecipe(self, input_tag, output_id):
        # type: (str, str) -> MachineRecipe
        return MachineRecipe({"item": {0: Input(input_tag, 1, is_tag=True)}}, {"item": {1: Output(output_id, 1)}}, self.power_cost, self.tick_duration)

    def SimpleXXTagRecipe(self, input_tag, input_count, output_id, output_count):
        # type: (str, int, str, int) -> MachineRecipe
        return MachineRecipe({"item": {0: Input(input_tag, input_count, is_tag=True)}}, {"item": {1: Output(output_id, output_count)}}, self.power_cost, self.tick_duration)


    def Recipe(self, inputs, outputs):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]]) -> MachineRecipe
        return MachineRecipe(
            inputs,
            outputs,
            self.power_cost,
            self.tick_duration
        )

    def ItemRecipe(self, inputs, outputs):
        # type: (dict[int, Input], dict[int, Output]) -> MachineRecipe
        return MachineRecipe(
            {"item": inputs},
            {"item": outputs},
            self.power_cost,
            self.tick_duration
        )
