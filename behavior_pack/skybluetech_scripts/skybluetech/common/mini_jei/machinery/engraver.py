# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery

from .define import CategoryType, Input, MachineRecipe, Output

OUTPUT_SLOT = 4


class EngraverRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.ENGRAVER

    def __init__(
        self,
        item_inputs,  # type: dict[int, Input]
        fluid_input,  # type: Input
        output_item_id,  # type: str
        output_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
        extra_fluid_input=None,  # type: Input | None
    ):
        # type: (...) -> None
        inputs = {CategoryType.ITEM: dict(item_inputs)}
        fluid_inputs = {0: fluid_input}  # type: dict[int, Input]
        if extra_fluid_input is not None:
            fluid_inputs[1] = extra_fluid_input
        inputs[CategoryType.FLUID] = fluid_inputs
        MachineRecipe.__init__(
            self,
            inputs,
            {CategoryType.ITEM: {OUTPUT_SLOT: Output(output_item_id, output_count)}},
            power_cost,
            tick_duration,
        )
        self.item_inputs = dict(item_inputs)
        self.fluid_input = fluid_input
        self.extra_fluid_input = extra_fluid_input
        self.output_item_id = output_item_id
        self.output_count = output_count

    def Marshal(self):
        return {
            "item_inputs": {
                str(slot): item.to_dict() for slot, item in self.item_inputs.items()
            },
            "fluid_input": self.fluid_input.to_dict(),
            "extra_fluid_input": (
                self.extra_fluid_input.to_dict()
                if self.extra_fluid_input is not None
                else None
            ),
            "output_item_id": self.output_item_id,
            "output_count": self.output_count,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        extra_fluid_input = data.get("extra_fluid_input")
        return cls(
            item_inputs={
                int(slot): Input.from_dict(item_data)
                for slot, item_data in data["item_inputs"].items()
            },
            fluid_input=Input.from_dict(data["fluid_input"]),
            output_item_id=data["output_item_id"],
            output_count=data["output_count"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
            extra_fluid_input=(
                Input.from_dict(extra_fluid_input)
                if extra_fluid_input is not None
                else None
            ),
        )
