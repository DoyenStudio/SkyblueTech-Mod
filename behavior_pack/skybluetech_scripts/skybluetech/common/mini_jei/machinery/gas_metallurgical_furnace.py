# coding=utf-8
from ...define.id_enum import GasMetallurgicalFurnace
from .define import MachineRecipe


class GasMetallurgicalFurnaceRecipe(MachineRecipe):
    recipe_icon_id = GasMetallurgicalFurnace.CONTROLLER

    def __init__(self, recipe_id, title, inputs, outputs, total_rf, tick_duration):
        self.recipe_id = recipe_id
        self.title = title
        self.total_rf = int(total_rf)
        MachineRecipe.__init__(
            self, inputs, outputs,
            power_cost=(self.total_rf + tick_duration - 1) // tick_duration,
            tick_duration=tick_duration,
        )

    def tick_cost(self, elapsed):
        # 累计向上取整的差额，TI9 的 133/134 RF 交替扣费仍恰好合计 20,000 RF。
        duration = self.tick_duration
        return ((self.total_rf * (elapsed + 1) + duration - 1) // duration
                - (self.total_rf * elapsed + duration - 1) // duration)

    def Marshal(self):
        data = MachineRecipe.Marshal(self)
        data.update(recipe_id=self.recipe_id, title=self.title, total_rf=self.total_rf)
        return data

    @classmethod
    def Unmarshal(cls, data):
        recipe = MachineRecipe.Unmarshal(data)
        return cls(data["recipe_id"], data["title"], recipe.inputs, recipe.outputs,
                   data["total_rf"], recipe.tick_duration)
