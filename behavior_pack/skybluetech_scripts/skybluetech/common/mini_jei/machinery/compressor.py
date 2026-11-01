# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ..core import UnmarshalOrderedInputs
from .define import CategoryType, MachineRecipe, Input, Output


class CompressorRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.COMPRESSOR

    def __init__(
        self, input_items, output_item, power_cost, tick_duration,
    ):
        # type: (dict[int, Input], Output, int, int) -> None
        # 单材料可放入任一输入槽，也可跨槽凑齐数量；多材料保留固定槽要求。
        unordered = len(input_items) == 1
        MachineRecipe.__init__(
            self,
            None if unordered else {CategoryType.ITEM: input_items},
            {CategoryType.ITEM: {3: output_item}},
            power_cost,
            tick_duration,
            inputs_unordered={
                CategoryType.ITEM: {(0, 1, 2): list(input_items.values())},
            } if unordered else None,
        )
        # 保留声明字典，用于既有的专用编解码格式。
        self.input_items = input_items
        self.output_item = output_item

    def Marshal(self):
        result = {
            "input_items": {str(k): v.to_dict() for k, v in self.input_items.items()},
            "output_item": self.output_item.to_dict(),
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> CompressorRecipe
        input_items = UnmarshalOrderedInputs(
            {CategoryType.ITEM: data["input_items"]}
        )[CategoryType.ITEM]
        return cls(
            input_items=input_items,
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
        return CompressorRecipe(
            {0: Input(input)}, Output(output), power_cost, tick_duration,
        )

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
            {0: Input(input, is_tag=True)}, Output(output), power_cost, tick_duration,
        )

    return generate_recipe
