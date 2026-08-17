# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from .define import MachineRecipe, Input, Output, CategoryType


class PrecisionCutterRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.PRECISION_CUTTER

    def __init__(
        self,
        input_item,  # type: Input
        output_items,  # type: dict[int, Output]
        cutter_level,  # type: int
        cutter_durability_cost,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        # type: (...) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: input_item}},
            {CategoryType.ITEM: output_items},
            power_cost,
            tick_duration,
        )
        self.input_item = input_item
        self.output_items = output_items
        self.cutter_level = cutter_level
        self.cutter_durability_cost = cutter_durability_cost

    def Marshal(self):
        # type: () -> dict
        # type: () -> dict
        return {
            "input_item": self.input_item.to_dict(),
            "output_items": {str(k): v.to_dict() for k, v in self.output_items.items()},
            "cutter_level": self.cutter_level,
            "cutter_durability_cost": self.cutter_durability_cost,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> PrecisionCutterRecipe
        return PrecisionCutterRecipe(
            input_item=Input.from_dict(data["input_item"]),
            output_items={
                int(slot_index): Output.from_dict(item_data)
                for slot_index, item_data in data["output_items"].items()
            },
            cutter_level=data["cutter_level"],
            cutter_durability_cost=data["cutter_durability_cost"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
