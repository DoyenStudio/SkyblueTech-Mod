# coding=utf-8
from ...define.id_enum import Machinery
from .define import CategoryType, MachineRecipe, Input, Output
from .distillation_column import _finite, integer_volume


class ThermalCrackerRecipe(MachineRecipe):
    """Fixed-slot continuous recipe; volumes and heat are rated per integer batch."""
    recipe_icon_id = Machinery.THERMAL_CRACKER

    def __init__(self, input_fluids, output_fluids, min_temperature,
                 fit_temperature, max_temperature, heat_cost, tick_duration=1):
        if tick_duration < 1 or int(tick_duration) != tick_duration:
            raise ValueError("Expected positive integer tick_duration")
        self.tick_duration = int(tick_duration)
        self.input_fluids = tuple((fid, integer_volume(v)) for fid, v in input_fluids)
        self.output_fluids = tuple((fid, integer_volume(v)) for fid, v in output_fluids)
        if len(self.input_fluids) != 2 or len(self.output_fluids) != 2:
            raise ValueError("Cracker requires two inputs and two outputs")
        self.min_temperature = _finite(min_temperature, "min temperature")
        self.fit_temperature = _finite(fit_temperature, "fit temperature", True)
        self.max_temperature = _finite(max_temperature, "max temperature", True)
        self.heat_cost = _finite(heat_cost, "heat cost", True)
        if not self.min_temperature < self.fit_temperature <= self.max_temperature:
            raise ValueError("Expected min < fit <= max temperature")
        MachineRecipe.__init__(self,
            {CategoryType.FLUID: dict((i, Input(fid, v)) for i, (fid, v) in enumerate(self.input_fluids))},
            {CategoryType.FLUID: dict((i + 2, Output(fid, v)) for i, (fid, v) in enumerate(self.output_fluids))},
            power_cost=0, tick_duration=self.tick_duration)

    def speed_at(self, temperature):
        if not self.min_temperature < temperature <= self.max_temperature:
            return 0.0
        return min(1.0, (temperature - self.min_temperature) / (self.fit_temperature - self.min_temperature))

    def Marshal(self):
        return dict(input_fluids=self.input_fluids, output_fluids=self.output_fluids,
                    min_temperature=self.min_temperature, fit_temperature=self.fit_temperature,
                    max_temperature=self.max_temperature, heat_cost=self.heat_cost,
                    tick_duration=self.tick_duration)

    @classmethod
    def Unmarshal(cls, data):
        return cls(**data)
