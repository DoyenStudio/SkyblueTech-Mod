# coding=utf-8
"""标称输出供配方索引使用；evaluate 计算温度下的实际进料、产物与热耗。"""
from math import isinf, isnan
from skybluetech_scripts.skybluetech.common.define.id_enum import DistillationColumn
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType, Input, MachineRecipe, Output,
)


def _finite(value, name, positive=False):
    value = float(value)
    if isnan(value) or isinf(value) or value < 0 or (positive and value == 0):
        raise ValueError("Invalid %s: %r" % (name, value))
    return value


def integer_volume(value):
    value = _finite(value, "fluid volume", True)
    rounded = int(round(value))
    if rounded <= 0 or abs(value - rounded) > 1e-9:
        raise ValueError("Recipe fluid volumes must be positive integer mB")
    return rounded


class DistillationFraction(object):
    def __init__(self, fluid_id, share, evap_start, evap_full, latent_heat):
        if not fluid_id:
            raise ValueError("Missing fraction fluid_id")
        self.fluid_id = fluid_id
        self.share = _finite(share, "share", True)
        self.evap_start = _finite(evap_start, "evap_start")
        self.evap_full = _finite(evap_full, "evap_full", True)
        self.latent_heat = _finite(latent_heat, "latent_heat")
        if self.evap_start >= self.evap_full:
            raise ValueError("evap_start must be below evap_full")

    def recovery(self, temperature):
        x = max(0.0, min(1.0, (temperature - self.evap_start) / (self.evap_full - self.evap_start)))
        return x * x * (3.0 - 2.0 * x)

    def Marshal(self):
        return dict(fluid_id=self.fluid_id, share=self.share,
                    evap_start=self.evap_start, evap_full=self.evap_full,
                    latent_heat=self.latent_heat)

    @classmethod
    def Unmarshal(cls, data):
        return cls(**data)


class DistillationPlan(object):
    def __init__(self, feed_volume, output_volumes, heat_cost):
        self.feed_volume = feed_volume
        self.output_volumes = tuple(output_volumes)
        self.heat_cost = heat_cost

    def scaled(self, scale):
        scale = _finite(scale, "scale")
        if scale > 1.0:
            raise ValueError("scale must not exceed one")
        return DistillationPlan(self.feed_volume * scale,
                                [v * scale for v in self.output_volumes],
                                self.heat_cost * scale)


class DistillationColumnRecipe(MachineRecipe):
    recipe_icon_id = DistillationColumn.CONTROLLER

    def __init__(self, input_fluid, input_volume, min_temperature,
                 fit_temperature, max_temperature, feed_heat_cost,
                 fractions, residue_fluid, tick_duration=1):
        if not input_fluid or not residue_fluid or input_fluid == residue_fluid:
            raise ValueError("Input and residue must be distinct fluid IDs")
        if tick_duration < 1 or int(tick_duration) != tick_duration:
            raise ValueError("Expected positive integer tick_duration")
        self.tick_duration = int(tick_duration)
        self.collection_name = input_fluid
        self.input_volume = integer_volume(input_volume)
        self.min_temperature = _finite(min_temperature, "min_temperature")
        self.fit_temperature = _finite(fit_temperature, "fit_temperature", True)
        # 保留旧配方参数及序列化格式；该值不再作为运行温度上限。
        self.max_temperature = _finite(max_temperature, "max_temperature", True)
        self.feed_heat_cost = _finite(feed_heat_cost, "feed_heat_cost")
        if not self.min_temperature < self.fit_temperature <= self.max_temperature:
            raise ValueError("Expected min < fit <= max temperature")
        # 脱离调用者的数据；同一配方可供多台机器共用。
        self.fractions = tuple(DistillationFraction.Unmarshal(f.Marshal()) for f in fractions)
        self.residue_fluid = residue_fluid
        if not 1 <= len(self.fractions) <= 3:
            raise ValueError("Expected 1..3 fractions plus residue (2..4 outputs)")
        if sum(f.share for f in self.fractions) >= 1.0:
            raise ValueError("Fraction shares must sum to less than one")
        for fraction in self.fractions:
            if fraction.evap_full > self.max_temperature:
                raise ValueError("Fraction cannot fully evaporate in operating range")
        for light, heavy in zip(self.fractions, self.fractions[1:]):
            if light.evap_start > heavy.evap_start or light.evap_full > heavy.evap_full:
                raise ValueError("Fractions must be ordered from light to heavy")
        self.output_fluids = tuple(f.fluid_id for f in self.fractions) + (residue_fluid,)
        if input_fluid in self.output_fluids or len(set(self.output_fluids)) != len(self.output_fluids):
            raise ValueError("Output fluids must be distinct and different from input")
        volumes = [self.input_volume * f.share for f in self.fractions]
        volumes.append(self.input_volume - sum(volumes))
        volumes = [integer_volume(volume) for volume in volumes]
        MachineRecipe.__init__(
            self, {CategoryType.FLUID: {0: Input(input_fluid, self.input_volume)}},
            {CategoryType.FLUID: dict((i + 1, Output(fid, volume))
                                     for i, (fid, volume) in enumerate(zip(self.output_fluids, volumes)))},
            power_cost=0, tick_duration=self.tick_duration,
        )

    def evaluate(self, temperature):
        # type: (float) -> DistillationPlan | None
        temperature = float(temperature)
        if isnan(temperature) or isinf(temperature) or temperature <= self.min_temperature:
            return None
        # 达到适宜温度后保持满速，继续按实际处理量扣热，不因高温停机。
        speed = min(1.0, (temperature - self.min_temperature) / (self.fit_temperature - self.min_temperature))
        feed = self.input_volume * speed / float(self.tick_duration)
        volumes = [feed * f.share * f.recovery(temperature) for f in self.fractions]
        heat = feed * self.feed_heat_cost + sum(v * f.latent_heat for v, f in zip(volumes, self.fractions))
        volumes.append(feed - sum(volumes))
        if any(isnan(v) or isinf(v) for v in [feed, heat] + volumes):
            raise ValueError("Distillation plan overflow")
        return DistillationPlan(feed, volumes, heat)

    def Marshal(self):
        return dict(input_fluid=self.collection_name, input_volume=self.input_volume,
                    min_temperature=self.min_temperature, fit_temperature=self.fit_temperature,
                    max_temperature=self.max_temperature, feed_heat_cost=self.feed_heat_cost,
                    fractions=[f.Marshal() for f in self.fractions], residue_fluid=self.residue_fluid,
                    tick_duration=self.tick_duration)

    @classmethod
    def Unmarshal(cls, data):
        values = dict(data)
        values["fractions"] = [DistillationFraction.Unmarshal(f) for f in data["fractions"]]
        return cls(**values)
