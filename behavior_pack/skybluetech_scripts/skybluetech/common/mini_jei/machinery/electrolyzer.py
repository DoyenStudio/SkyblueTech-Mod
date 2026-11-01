# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType, MachineRecipe, Input, Output,
)


class ElectrolyzerRecipe(MachineRecipe):
    recipe_icon_id = Machinery.ELECTROLYZER

    def __init__(
        self,
        input_fluid,
        input_volume,
        output_fluid1,
        output_volume1,
        output_fluid2,
        output_volume2,
        power_cost,
        tick_duration,
        input_item=None,
        output_item=None,
        byproduct=None,
        output_fluid3=None,
        output_volume3=0,
    ):
        # type: (str, float, str, float, str, float, int, int, Input | None, Output | None, Output | None, str | None, float) -> None
        # Fluid slots: 1 cathode upper, 2 anode, 3 cathode lower (optional).
        inputs = {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}}
        outputs = {CategoryType.FLUID: {
            1: Output(output_fluid1, output_volume1),
            2: Output(output_fluid2, output_volume2),
        }}
        if output_fluid3 is not None:
            if output_volume3 <= 0:
                raise ValueError("output_volume3 must be positive when output_fluid3 is set")
            outputs[CategoryType.FLUID][3] = Output(output_fluid3, output_volume3)
        if input_item is not None:
            inputs[CategoryType.ITEM] = {0: input_item}
        item_outputs = {}
        if output_item is not None:
            item_outputs[1] = output_item
        if byproduct is not None:
            item_outputs[2] = byproduct
        if item_outputs:
            outputs[CategoryType.ITEM] = item_outputs
        MachineRecipe.__init__(
            self,
            inputs,
            outputs,
            power_cost,
            tick_duration,
        )
        self.input_fluid = input_fluid
        self.input_volume = input_volume
        self.output_fluid1 = output_fluid1
        self.output_volume1 = output_volume1
        self.output_fluid2 = output_fluid2
        self.output_volume2 = output_volume2
        self.output_fluid3 = output_fluid3
        self.output_volume3 = output_volume3
        self.input_item = input_item
        self.output_item = output_item
        self.byproduct = byproduct

    def Marshal(self):
        # type: () -> dict
        result = {
            "input_fluid": self.input_fluid,
            "input_volume": self.input_volume,
            "output_fluid1": self.output_fluid1,
            "output_volume1": self.output_volume1,
            "output_fluid2": self.output_fluid2,
            "output_volume2": self.output_volume2,
            "output_fluid3": self.output_fluid3,
            "output_volume3": self.output_volume3,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
            "input_item": self.input_item.to_dict() if self.input_item is not None else None,
            "output_item": self.output_item.to_dict() if self.output_item is not None else None,
            "byproduct": self.byproduct.to_dict() if self.byproduct is not None else None,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_fluid1=data["output_fluid1"],
            output_volume1=data["output_volume1"],
            output_fluid2=data["output_fluid2"],
            output_volume2=data["output_volume2"],
            output_fluid3=data.get("output_fluid3"),
            output_volume3=data.get("output_volume3", 0),
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
            input_item=Input.from_dict(data["input_item"]) if data.get("input_item") is not None else None,
            output_item=Output.from_dict(data["output_item"]) if data.get("output_item") is not None else None,
            byproduct=Output.from_dict(data["byproduct"]) if data.get("byproduct") is not None else None,
        )
