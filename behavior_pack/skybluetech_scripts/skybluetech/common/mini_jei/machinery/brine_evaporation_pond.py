# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import BrineEvaporationPond
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType,
    Input,
    MachineRecipe,
    Output,
)


class BrineEvaporationPondRecipe(MachineRecipe):
    recipe_icon_id = BrineEvaporationPond.CONTROLLER

    def __init__(
        self,
        input_fluid,  # type: str
        input_volume,  # type: float
        output_fluid,  # type: str
        output_volume,  # type: float
        min_temperature,  # type: float
        fit_temperature,  # type: float
        heat_cost,  # type: float
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: {1: Output(output_fluid, output_volume)}},
            0,
            1,
        )
        self.collection_name = input_fluid
        self.consume = input_volume
        self.produce = output_volume
        self.produce_matter = output_fluid
        self.min_temperature = min_temperature
        self.fit_temperature = fit_temperature
        # 最适温度下每 tick 完整处理一次的热耗, 与液量按同一倍率缩放。
        self.heat_cost = heat_cost

    def Marshal(self):
        # type: () -> dict
        return {
            "input_fluid": self.collection_name,
            "input_volume": self.consume,
            "output_fluid": self.produce_matter,
            "output_volume": self.produce,
            "min_temperature": self.min_temperature,
            "fit_temperature": self.fit_temperature,
            "heat_cost": self.heat_cost,
        }

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> BrineEvaporationPondRecipe
        return cls(
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_fluid=data["output_fluid"],
            output_volume=data["output_volume"],
            min_temperature=data["min_temperature"],
            fit_temperature=data["fit_temperature"],
            heat_cost=data["heat_cost"],
        )
