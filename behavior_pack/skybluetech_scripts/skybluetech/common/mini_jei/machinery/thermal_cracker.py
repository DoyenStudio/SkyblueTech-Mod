# coding=utf-8
from ...define.id_enum import Machinery
from .define import CategoryType, MachineRecipe, Input, Output
from .distillation_column import _finite, integer_volume


class ThermalCrackerRecipe(MachineRecipe):
    recipe_icon_id = Machinery.THERMAL_CRACKER

    def __init__(self, input_fluids, output_fluids, min_temperature,
                 fit_temperature, max_temperature, heat_cost, tick_duration=1,
                 recipe_id="", solid_in=None, solid_out=None, solid_in_is_tag=False):
        duration = int(tick_duration)
        if duration < 1 or duration != tick_duration:
            raise ValueError("Expected positive integer tick_duration")
        self.recipe_id = str(recipe_id)
        self.solid_in_is_tag = solid_in_is_tag
        self.input_fluids = tuple((str(fid), integer_volume(v)) for fid, v in input_fluids)
        self.output_fluids = tuple((str(fid), integer_volume(v)) for fid, v in output_fluids)
        if len(self.output_fluids) != 2:
            raise ValueError("Cracker requires two output fluids")
        self.min_temperature = _finite(min_temperature, "min temperature")
        self.fit_temperature = _finite(fit_temperature, "fit temperature")
        self.max_temperature = (
            None if self.recipe_id and max_temperature is None
            else _finite(max_temperature, "max temperature")
        )
        self.heat_cost = _finite(heat_cost, "heat cost", True)
        if (self.min_temperature >= self.fit_temperature or
                (self.max_temperature is not None and self.fit_temperature > self.max_temperature)):
            raise ValueError("Expected min < fit <= max temperature")
        inputs = {CategoryType.FLUID: dict(
            (slot, Input(fid, volume)) for slot, (fid, volume) in enumerate(self.input_fluids))}
        outputs = {CategoryType.FLUID: dict(
            (slot, Output(fid, volume)) for slot, (fid, volume) in enumerate(self.output_fluids, 2))}
        if self.recipe_id:
            if solid_in is None or solid_out is None or not 1 <= len(self.input_fluids) <= 2:
                raise ValueError("Cracker batches require solid input and output and one or two input fluids")
            self.solid_in = (str(solid_in[0]), integer_volume(solid_in[1]))
            self.solid_out = (str(solid_out[0]), integer_volume(solid_out[1]))
            solid_id, count = self.solid_in
            inputs[CategoryType.ITEM] = {0: Input(solid_id, count, is_tag=self.solid_in_is_tag)}
            outputs[CategoryType.ITEM] = {1: Output(*self.solid_out)}
        else:
            if len(self.input_fluids) != 2 or solid_in is not None or solid_out is not None:
                raise ValueError("Continuous cracking requires two input fluids and no solids")
            self.solid_in = self.solid_out = None
        MachineRecipe.__init__(self, inputs, outputs, power_cost=0, tick_duration=duration)

    def speed_at(self, temperature):
        if (temperature <= self.min_temperature or
                (self.max_temperature is not None and temperature > self.max_temperature)):
            return 0.0
        return min(1.0, (temperature - self.min_temperature) / (self.fit_temperature - self.min_temperature))

    def conditions(self):
        if self.recipe_id:
            return [
                "%s 整批加工；满速 %d tick" % (self.recipe_id.split(":", 1)[0].upper(), self.tick_duration),
                "%g K 起步；%g K 满速" % (self.min_temperature, self.fit_temperature),
                "每批耗热 %g RF热；外部供热；任一出口堵塞均暂停" % self.heat_cost,
            ]
        return [
            "连续加工；满速 %d tick 等效处理一份" % self.tick_duration,
            "%g K < T ≤ %g K；%g K 满速" % (
                self.min_temperature, self.max_temperature, self.fit_temperature),
            "每份耗热 %g RF热；外部供热；任一出口堵塞均暂停" % self.heat_cost,
        ]

    def Marshal(self):
        data = dict(input_fluids=self.input_fluids, output_fluids=self.output_fluids,
                    min_temperature=self.min_temperature, fit_temperature=self.fit_temperature,
                    max_temperature=self.max_temperature, heat_cost=self.heat_cost,
                    tick_duration=self.tick_duration)
        if self.recipe_id:
            data.update(recipe_id=self.recipe_id, solid_in=self.solid_in, solid_out=self.solid_out)
            if self.solid_in_is_tag:
                data["solid_in_is_tag"] = True
        return data

    @classmethod
    def Unmarshal(cls, data):
        return cls(**data)
