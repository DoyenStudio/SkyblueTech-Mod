# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output
from .distillation_column import integer_volume


class DistillationChamberRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.DISTILLATION_CHAMBER

    def __init__(
        self,
        input_fluid,  # type: str
        input_volume,  # type: float
        output_fluid,  # type: str
        output_volume,  # type: float
        min_temperature,  # type: float
        fit_temperature,  # type: float
        max_temperature,  # type: float
        heat_per_produce=1.0,  # type: float
        tick_duration=1,
    ):
        if tick_duration < 1 or int(tick_duration) != tick_duration:
            raise ValueError("Expected positive integer tick_duration")
        input_volume = integer_volume(input_volume)
        output_volume = integer_volume(output_volume)
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: {1: Output(output_fluid, output_volume)}},
            0,
            int(tick_duration),
        )
        self.collection_name = input_fluid
        self.consume = input_volume
        self.produce = output_volume
        self.produce_matter = output_fluid
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.fit_temperature = fit_temperature
        # 每产出 1 mB 产物要从本机热值里扣掉多少 RF 热, 单位 RF热/mB, 默认 1.0。
        # 调大它 = 同样产量要多掏热, 也就需要加热仓比最适温度高出一截才推得动。
        self.heat_per_produce = heat_per_produce

    def Marshal(self):
        # type: () -> dict
        result = {
            "tick_duration": self.tick_duration,
            "input_fluid": self.collection_name,
            "input_volume": self.consume,
            "output_fluid": self.produce_matter,
            "output_volume": self.produce,
            "min_temperature": self.min_temperature,
            "fit_temperature": self.fit_temperature,
            "max_temperature": self.max_temperature,
            "heat_per_produce": self.heat_per_produce,
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> DistillationChamberRecipe
        return cls(
            tick_duration=data.get("tick_duration", 1),
            input_fluid=data["input_fluid"],
            input_volume=data["input_volume"],
            output_fluid=data["output_fluid"],
            output_volume=data["output_volume"],
            min_temperature=data["min_temperature"],
            fit_temperature=data["fit_temperature"],
            max_temperature=data["max_temperature"],
            heat_per_produce=data["heat_per_produce"],
        )


c2k = lambda c: c + 273
