# coding=utf-8
#
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from ...define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class FreezerRecipe(MachineRecipe):
    recipe_icon_id = machinery.FREEZER
    render_ui_def_name = "RecipeCheckerLib.freezer_recipes"

    def __init__(
        self,
        index,  # type: int
        input_fluid,  # type: str
        input_volume,  # type: float
        output_item,  # type: str
        output_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.ITEM: {0: Output(output_item, output_count)}},
            power_cost,
            tick_duration,
        )
        self.index = index
        self.input_fluid = input_fluid
        self.input_volume = input_volume
        self.output_item = output_item
        self.output_count = output_count

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipe.RenderInit(self, panel)
        panel["fake_btn/item_renderer"].asItemRenderer().SetUiItem(
            Item(self.output_item)
        )

    def Marshal(self):
        return {
            "index": self.index,
            "input_fluid": self.input_fluid,
            "input_volume": self.input_volume,
            "output_item": self.output_item,
            "output_count": self.output_count,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            index=data["index"],
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_item=data["output_item"],
            output_count=data["output_count"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
