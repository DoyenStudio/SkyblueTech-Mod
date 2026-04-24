# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from ....common.define.id_enum import machinery
from ..core import MarshalInputs, MarshalOutputs, UnmarshalInputs, UnmarshalOutputs
from .define import CategoryType, MachineRecipe, Input, Output


class AlloyFurnaceRecipe(MachineRecipe):
    recipe_icon_id = machinery.ALLOY_FURNACE
    render_ui_def_name = "RecipeCheckerLib.alloy_furnace_recipes"

    def __init__(self, item_inputs, item_outputs, power_cost, tick_duration):
        # type: (dict[int, Input], dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: item_inputs},
            {CategoryType.ITEM: item_outputs},
            power_cost,
            tick_duration,
        )
        self.item_inputs = item_inputs
        self.item_outputs = item_outputs

    def Marshal(self):
        # type: () -> dict
        return {
            "item_inputs": MarshalInputs({CategoryType.ITEM: self.item_inputs}),
            "item_outputs": MarshalOutputs({CategoryType.ITEM: self.item_outputs}),
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> AlloyFurnaceRecipe
        return AlloyFurnaceRecipe(
            item_inputs=UnmarshalInputs(data["inputs"])[CategoryType.ITEM],
            item_outputs=UnmarshalOutputs(data["outputs"])[CategoryType.ITEM],
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
        return AlloyFurnaceRecipe(inputs, outputs, power_cost, tick_duration)

    return generate_recipe
