# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import CommonLiquid, Machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import CategoryType, MachineRecipe


class IndustrialCentrifugeRecipe(MachineRecipe):
    recipe_icon_id = Machinery.INDUSTRIAL_CENTRIFUGE

    def __init__(self, *args, **kwargs):
        self.min_temperature, self.fit_temperature, self.heat_cost = kwargs.pop(
            "heat", (0, 0, 0)
        )
        MachineRecipe.__init__(self, *args, **kwargs)

    def heat_conditions(self):
        if not self.heat_cost:
            return []
        lines = ["底面供热，%d K 起步，%d K 满速" % (
            self.min_temperature, self.fit_temperature),
            "每批耗热 %d RF热" % self.heat_cost]
        if self.inputs[CategoryType.FLUID][0].id == CommonLiquid.CALCIUM_CHLORIDE:
            lines.append("每两批结晶 1 份氯化钙粉，每批产水 400 mB")
        return lines

    def Marshal(self):
        data = MachineRecipe.Marshal(self)
        data["heat"] = (self.min_temperature, self.fit_temperature, self.heat_cost)
        return data

    @classmethod
    def Unmarshal(cls, data):
        recipe = super(IndustrialCentrifugeRecipe, cls).Unmarshal(data)
        recipe.min_temperature, recipe.fit_temperature, recipe.heat_cost = data["heat"]
        return recipe
