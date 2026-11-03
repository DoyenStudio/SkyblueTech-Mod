# coding=utf-8
from ...define.id_enum import Machinery
from .define import CategoryType, MachineRecipe, Input, Output


class HeatMeltingChamberRecipe(MachineRecipe):
    recipe_icon_id = Machinery.HEAT_MELTING_CHAMBER

    def __init__(self, input_item_id, output_fluid, output_volume,
                 tick_duration, min_temperature, fit_temperature, max_temperature,
                 output_item_id=None, output_count=1, heat_per_produce=1.0):
        if not (0 <= min_temperature < fit_temperature <= max_temperature):
            raise ValueError("Expected 0 <= min < fit <= max temperature")
        if tick_duration <= 0 or output_volume <= 0 or heat_per_produce < 0:
            raise ValueError("Invalid duration, volume or heat cost")
        if output_count <= 0 or int(output_count) != output_count:
            raise ValueError("Output count must be a positive integer")
        outputs = {CategoryType.FLUID: {0: Output(output_fluid, output_volume)}}
        item_outputs = {}
        if output_item_id is not None:
            item_outputs = {CategoryType.ITEM: {1: Output(output_item_id, int(output_count))}}
            outputs.update(item_outputs)
        inputs = {CategoryType.ITEM: {0: Input(input_item_id, 1)}}
        MachineRecipe.__init__(self, inputs, outputs, 0, tick_duration)
        # 过热仍消耗输入并产生固体，仅跳过流体容量检查及流体产出。
        self.overheated_recipe = MachineRecipe(inputs, item_outputs, 0, tick_duration)
        self.input_item_id = input_item_id
        self.output_fluid = output_fluid
        self.output_volume = output_volume
        self.output_item_id = output_item_id
        self.output_count = int(output_count)
        self.min_temperature = min_temperature
        self.fit_temperature = fit_temperature
        self.max_temperature = max_temperature
        self.heat_per_produce = heat_per_produce

    def Marshal(self):
        return dict((key, getattr(self, key)) for key in (
            "input_item_id", "output_fluid", "output_volume", "tick_duration",
            "min_temperature", "fit_temperature", "max_temperature",
            "output_item_id", "output_count", "heat_per_produce"))

    @classmethod
    def Unmarshal(cls, data):
        return cls(**data)
