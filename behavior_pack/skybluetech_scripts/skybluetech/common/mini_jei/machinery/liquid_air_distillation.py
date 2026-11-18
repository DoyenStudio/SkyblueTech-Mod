# coding=utf-8
from math import isnan, isinf
from ...define.id_enum import fluids
from .define import MachineRecipe, Input, Output
from .distillation_column import DistillationColumnRecipe, DistillationPlan


class LiquidAirDistillationRecipe(DistillationColumnRecipe):
    """保留压缩空气液化的 16:1 体积比，三气始终同比产出。"""
    required_output_ports = 3

    def __init__(self):
        self.collection_name = fluids.CommonLiquid.LIQUID_AIR
        self.input_volume = 25
        self.min_temperature = 75.0
        self.fit_temperature = 95.0
        self.max_temperature = 900.0
        self.heat_cost = 200.0
        self.output_fluids = (fluids.CommonGas.NITROGEN, fluids.CommonGas.ARGON, fluids.CommonGas.OXYGEN)
        self.output_volumes = (312, 4, 84)
        MachineRecipe.__init__(
            self, {"fluid": {0: Input(self.collection_name, self.input_volume)}},
            {"fluid": dict((i + 1, Output(fid, amount))
                           for i, (fid, amount) in enumerate(zip(self.output_fluids, self.output_volumes)))},
            power_cost=0, tick_duration=200,
        )

    def evaluate(self, temperature):
        if isnan(temperature) or isinf(temperature) or temperature <= self.min_temperature:
            return None
        scale = min(1.0, (temperature - self.min_temperature) / (self.fit_temperature - self.min_temperature)) / self.tick_duration
        return DistillationPlan(self.input_volume * scale,
                                [v * scale for v in self.output_volumes], self.heat_cost * scale)

    def Marshal(self):
        return {}

    @classmethod
    def Unmarshal(cls, data):
        return cls()
