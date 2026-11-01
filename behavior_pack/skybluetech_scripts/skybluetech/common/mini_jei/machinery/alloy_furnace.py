# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ..core import MarshalOrderedInputs, MarshalOrderedOutputs, UnmarshalOrderedInputs, UnmarshalOrderedOutputs
from .define import CategoryType, MachineRecipe, Input, Output


class AlloyFurnaceRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.ALLOY_FURNACE

    def __init__(
        self, item_inputs, item_outputs, power_cost, tick_duration,
    ):
        # type: (dict[int, Input], dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            outputs={CategoryType.ITEM: item_outputs},
            power_cost=power_cost,
            tick_duration=tick_duration,
            inputs_unordered={
                CategoryType.ITEM: {
                    (0, 1, 2, 3): [item_inputs[slot] for slot in sorted(item_inputs)],
                },
            },
        )
        # 保留原构造参数和专用编解码格式。输入字典键只决定展示顺序，
        # 输出字典键仍指定实际产出槽位。
        self.item_inputs = item_inputs
        self.item_outputs = item_outputs

    def Marshal(self):
        # type: () -> dict
        result = {
            "item_inputs": MarshalOrderedInputs({CategoryType.ITEM: self.item_inputs}),
            "item_outputs": MarshalOrderedOutputs({CategoryType.ITEM: self.item_outputs}),
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> AlloyFurnaceRecipe
        return cls(
            item_inputs=UnmarshalOrderedInputs(data["item_inputs"])[CategoryType.ITEM],
            item_outputs=UnmarshalOrderedOutputs(data["item_outputs"])[CategoryType.ITEM],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )


def gen_preset_recipe(
    power_cost,  # type: int
    tick_duration,  # type: int
):
    def generate_recipe(
        inputs,  # type: dict[int, Input]
        outputs,  # type: dict[int, Output]
    ):
        return AlloyFurnaceRecipe(
            inputs, outputs, power_cost, tick_duration,
        )

    return generate_recipe
