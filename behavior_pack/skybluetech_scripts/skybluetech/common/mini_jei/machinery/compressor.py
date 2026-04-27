# coding=utf-8
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class CompressorRecipe(MachineRecipe):
    recipe_icon_id = machinery.COMPRESSOR

    def __init__(self, input_item, output_item, power_cost, tick_duration):
        # type: (Input, Output, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: input_item}},
            {CategoryType.ITEM: {1: output_item}},
            power_cost,
            tick_duration,
        )
        self.input_item = input_item
        self.output_item = output_item

    def Marshal(self):
        return {
            "input_item": self.input_item.to_dict(),
            "output_item": self.output_item.to_dict(),
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> CompressorRecipe
        return CompressorRecipe(
            input_item=Input.from_dict(data["input_item"]),
            output_item=Output.from_dict(data["output_item"]),
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )


def gen_preset_recipe(
    power_cost,  # type: int
    tick_duration,  # type: int
):
    def generate_recipe(
        input,  # type: str
        output,  # type: str
    ):
        return CompressorRecipe(Input(input), Output(output), power_cost, tick_duration)

    return generate_recipe


def gen_preset_tagged_recipe(
    power_cost,  # type: int
    tick_duration,  # type: int
):
    def generate_recipe(
        input,  # type: str
        output,  # type: str
    ):
        return CompressorRecipe(
            Input(input, is_tag=True), Output(output), power_cost, tick_duration
        )

    return generate_recipe
