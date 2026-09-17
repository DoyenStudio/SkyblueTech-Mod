# coding=utf-8
from ...define.id_enum import Machinery, VacuumFreezer
from ...define.tag_enum import IngotTag
from .define import CategoryType, Input, MachineRecipe, Output, RecipesCollection


class VacuumFreezerRecipe(MachineRecipe):
    # 真空冷却仓配方。

    # 这类配方比普通机器配方多两个概念, 都是"温度"带来的:

    #     - 温度窗口: 高于 `max_temperature` 时配方不但不推进, 进度还会按同一条温度
    #       曲线倒退(温度越高退得越快, 最快 1 tick 退掉 1 tick 的进度), 相当于"还没冷
    #       到能液化"; 低于 `fit_temperature` 时按最快速度推进, 中间则按比例线性变慢。
    #     - 自身放热: 每推进一点就往机器热值里加 `tick_heat_value_add`(按推进速率
    #       折扣), 这份热量不是白给的, 由机器的制冷机搬走, 温度越低搬走它越费电。

    # 计时方式: `ticks_left` 每 tick 减少"本 tick 的推进速率"(0~1), 所以 `max_tick_duration`
    # 就是温度足够低时的最少耗时; 跑完一次后 `ticks_left` 会加上原时长重新开始, 也就是
    # 这个配方是"一份原料一份产出"循环执行, 而不是一直烧。

    # 注意 `power_cost` 恒为 0: 配方本身不直接吃电, 耗电全部体现在制冷机搬热上。
    recipe_icon_id = VacuumFreezer.CONTROLLER

    def __init__(
        self,
        input_item=None,  # type: Input | None
        input_fluid=None,  # type: Input | None
        output_item=None,  # type: Output | None
        output_fluid=None,  # type: Output | None
        max_temperature=300,  # type: float
        fit_temperature=200,  # type: float
        max_tick_duration=200,  # type: int
        tick_heat_value_add=1,  # type: float
        extra_upgrader_id=None,  # type: str | None
    ):
        inputs = {}  # type: dict[str, dict[int, Input]]
        outputs = {}  # type: dict[str, dict[int, Output]]
        if input_item is not None:
            inputs[CategoryType.ITEM] = {0: input_item}
        if output_item is not None:
            outputs[CategoryType.ITEM] = {1: output_item}
        if input_fluid is not None:
            inputs[CategoryType.FLUID] = {0: input_fluid}
        if output_fluid is not None:
            outputs[CategoryType.FLUID] = {1: output_fluid}
        MachineRecipe.__init__(
            self, inputs, outputs, power_cost=0, tick_duration=max_tick_duration
        )
        self.input_item = input_item
        self.input_fluid = input_fluid
        self.output_item = output_item
        self.output_fluid = output_fluid
        self.max_temperature = max_temperature
        self.fit_temperature = fit_temperature
        self.max_tick_duration = max_tick_duration
        self.tick_heat_value_add = tick_heat_value_add
        self.extra_upgrader_id = extra_upgrader_id

    def GetRateAtKelvin(self, kelvin):
        # type: (float) -> float
        # 返回本配方在温度 `kelvin`(K) 下的推进速率, 取值 0~1, 含义是"每 tick 能推进多少个
        # tick 的进度":

        #     - 高于 `max_temperature`: 0, 完全不推进(进度此时是倒退的, 见 `GetSignedRateAtKelvin`)
        #     - 低于 `fit_temperature`: 1, 按 `max_tick_duration` 的最快速度推进
        #     - 中间按温度线性插值, 温度每高 1K 就慢一点

        # 客户端 UI 的"配方效率"读数用它, 那个读数问的是"离最适温度有多近", 负速率没法显示,
        # 所以这里只截取温度曲线的正半轴; 机器端推进进度用的是带符号的原曲线。
        return max(0.0, self.GetSignedRateAtKelvin(kelvin))

    def GetSignedRateAtKelvin(self, kelvin):
        # type: (float) -> float
        # 带符号的推进速率, 取值 -1~1, 正反向共用同一条直线:

        #     - 低于 `fit_temperature`: 1, 按 `max_tick_duration` 的最快速度推进
        #     - 等于 `max_temperature`: 0, 停在原地
        #     - 高于 `max_temperature`: 负值, 进度以该速率倒退

        # 两个方向都在满速处截断: 超出窗口边界的部分按窗口宽度 `t_range` 线性外推, 推满一个
        # 窗口宽度就是满速, 再往外不再变快。所以倒退最坏也只是"1 tick 退 1 tick 的进度",
        # 清空一份进度至少要 `max_tick_duration` 个 tick; 温度越贴近 `max_temperature` 退得越慢,
        # 不会像"超出即清零"那样抖一下就损失整份进度。
        rate = (self.max_temperature - kelvin) / (
            self.max_temperature - self.fit_temperature
        )
        return min(max(rate, -1.0), 1.0)

    def Marshal(self):
        return {
            "input_item": self.input_item.to_dict() if self.input_item else None,
            "input_fluid": self.input_fluid.to_dict() if self.input_fluid else None,
            "output_item": self.output_item.to_dict() if self.output_item else None,
            "output_fluid": self.output_fluid.to_dict() if self.output_fluid else None,
            "max_temperature": self.max_temperature,
            "fit_temperature": self.fit_temperature,
            "max_tick_duration": self.max_tick_duration,
            "tick_heat_value_add": self.tick_heat_value_add,
            "extra_upgrader_id": self.extra_upgrader_id,
        }

    @classmethod
    def Unmarshal(cls, dct):
        return cls(
            input_item=Input.from_dict(dct["input_item"])
            if dct["input_item"]
            else None,
            input_fluid=Input.from_dict(dct["input_fluid"])
            if dct["input_fluid"]
            else None,
            output_item=Output.from_dict(dct["output_item"])
            if dct["output_item"]
            else None,
            output_fluid=Output.from_dict(dct["output_fluid"])
            if dct["output_fluid"]
            else None,
            max_temperature=dct["max_temperature"],
            fit_temperature=dct["fit_temperature"],
            max_tick_duration=dct["max_tick_duration"],
            tick_heat_value_add=dct["tick_heat_value_add"],
            # 旧数据里没有这个键, 缺省按"不需要升级卡"处理
            extra_upgrader_id=dct.get("extra_upgrader_id"),
        )
