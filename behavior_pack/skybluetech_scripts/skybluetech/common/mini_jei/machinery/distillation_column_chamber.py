# coding=utf-8
"""将小型蒸馏仓配方按八倍吞吐注册到蒸馏塔的配方与展示体系。"""
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType, Input, MachineRecipe, Output,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_chamber import DistillationChamberRecipe
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_column import (
    DistillationColumnRecipe, DistillationPlan,
)


class DistillationColumnChamberRecipe(DistillationColumnRecipe):
    chamber_multiplier = 8

    def __init__(self, chamber_recipe):
        self.chamber_recipe = chamber_recipe
        self.collection_name = chamber_recipe.collection_name
        self.min_temperature = chamber_recipe.min_temperature
        self.fit_temperature = chamber_recipe.fit_temperature
        self.max_temperature = chamber_recipe.max_temperature
        self.output_fluids = (chamber_recipe.produce_matter,)
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(self.collection_name, chamber_recipe.consume * self.chamber_multiplier)}},
            {CategoryType.FLUID: {1: Output(chamber_recipe.produce_matter, chamber_recipe.produce * self.chamber_multiplier)}},
            power_cost=0, tick_duration=chamber_recipe.tick_duration,
        )

    def evaluate(self, temperature):
        plan = self.chamber_recipe.evaluate(temperature)
        if plan is None:
            return None
        return DistillationPlan(
            plan.feed_volume * self.chamber_multiplier,
            [volume * self.chamber_multiplier for volume in plan.output_volumes],
            plan.heat_cost * self.chamber_multiplier,
        )

    def Marshal(self):
        return {"chamber_recipe": self.chamber_recipe.Marshal()}

    @classmethod
    def Unmarshal(cls, data):
        return cls(DistillationChamberRecipe.Unmarshal(data["chamber_recipe"]))
