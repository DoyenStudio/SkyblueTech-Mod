# coding=utf-8
from ...define.id_enum import LargeReactionPool
from .define import MachineRecipe


class LargeReactionPoolRecipe(MachineRecipe):
    recipe_icon_id = LargeReactionPool.CONTROLLER

    def __init__(self, recipe_id, title, inputs, outputs, power_cost, tick_duration, heat=(0, 0, 0)):
        MachineRecipe.__init__(self, inputs, outputs, power_cost, tick_duration)
        self.recipe_id = recipe_id
        self.title = title
        self.min_temperature, self.fit_temperature, self.heat_cost = heat

    def conditions(self):
        lines = [self.title, "整批耗电 %d RF" % (self.power_cost * self.tick_duration)]
        if self.heat_cost:
            lines.append("热口供热  %d K 起步 / %d K 满速" % (self.min_temperature, self.fit_temperature))
            lines.append("每批耗热 %d RF热" % self.heat_cost)
        return lines

    def Marshal(self):
        data = MachineRecipe.Marshal(self)
        data.update(recipe_id=self.recipe_id, title=self.title,
                    heat=(self.min_temperature, self.fit_temperature, self.heat_cost))
        return data

    @classmethod
    def Unmarshal(cls, data):
        base = MachineRecipe.Unmarshal(data)
        # Python 2 的 JSON 产生 unicode，原生方块实体只能保存 str 型物料 ID。
        for groups in (base.inputs, base.outputs):
            for slots in groups.values():
                for entry in slots.values():
                    entry.id = str(entry.id)
        title = data["title"]
        if not isinstance(title, str):
            title = title.encode("utf-8")
        return cls(str(data["recipe_id"]), title, base.inputs, base.outputs,
                   base.power_cost, base.tick_duration, data["heat"])
