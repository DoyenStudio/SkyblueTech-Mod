# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum import Machinery
from ...common.events.machinery.electric_heater import ElectricHeaterSubmitModifiesEvent
from ...common.machinery_def.electric_heater import (
    K_CURRENT_POWER,
    K_KELVIN_LIMIT,
    K_MAX_POWER,
    MAX_HEAT_VALUE,
    MAX_KELVIN,
    MAX_POWER,
    MIN_KELVIN,
    STORE_RF_MAX,
)
from .basic import (
    GUIControl,
    HeatCtrl,
    OperationListener,
    PowerControl,
    RegisterMachine,
)


@RegisterMachine
class ElectricHeater(HeatCtrl, GUIControl, PowerControl, OperationListener):
    """
    电力加热仓。

    玩家设定最大功率(`max_power`, RF/t)与目标温度(`kelvin_limit`, K)。玩家设定的是每个
    结算周期的电预算, 本机按全包的电→热标准单价(`HeatCtrl.electric_per_heat`, 默认
    `Thermal.ELECTRIC_PER_HEAT`)把它换成本周期的产热功率, 该值即
    `Thermal.HeatToTarget` 的 `max_power` 参数。

    电费按设定功率全额结算, 而实际进到本机的热量由 "距目标还差多少" 钳位: 温差不够时
    多出来的热量进不来, 电却照付。功率开得远超所需时这部分就是白烧 —— 过量的热会把
    物料直接蒸散掉, 所以功率要按需给, 不要一味拉满。

    产热、环境散热与热扩散全部委托给 `HeatCtrl` 的 `phys_math.Thermal` 实现,
    本类只按电预算与温度决定本周期的 `heat_power`。
    """

    block_name = Machinery.ELECTRIC_HEATER
    store_rf_max = STORE_RF_MAX
    max_heat_value = MAX_HEAT_VALUE
    spread_heat = True

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._cached_max_power = self.bdata[K_MAX_POWER] or 0
        self.running_power = self._cached_max_power * self.WORK_INTERVAL
        self.bdata[K_CURRENT_POWER] = 0

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def OnHeatWork(self):
        # type: () -> None
        """
        按玩家设定的功率产热, 并按设定功率全额结算电费。

        只有电量足够、且本机温度还没到玩家设定温度时才产热, 其余情况置 0。这里必须
        无条件调用 `PowerEnough()`: 机器停机期间本方法仍会被调用, 这是 "能量不足"
        停机旗唯一能解除的时机。

        注意扣电在钳位之前: 本周期该产的热由 `Thermal.HeatToTarget` 按 "距目标还差多少"
        钳位, 但电费按 `running_power` 全额扣。温差不够时没进来的那部分热量就是白烧,
        这是有意为之(见类文档)。
        """
        if not self.PowerEnough() or self.kelvin >= self.heat_target_kelvin:
            self.SetOutputHeatPower(0.0)
            self._set_current_power(0.0)
            return
        self.ReducePower()
        self.SetOutputHeatPower(self.HeatFromElectric(self.running_power))
        self._set_current_power(self.max_power)

    def _set_current_power(self, power):
        # type: (float) -> None
        "写 UI 用的实时功率; 值没变则跳过 NBT 写入。"
        if (self.bdata[K_CURRENT_POWER] or 0) != power:
            self.bdata[K_CURRENT_POWER] = power

    @property
    def heat_target_kelvin(self):
        # type: () -> float
        "产热目标温度, 即玩家设定的最高温度。"
        return self.kelvin_limit

    def set_power(self, power):
        # type: (int) -> None
        self.max_power = min(max(power, 0), MAX_POWER)

    def set_kelvin_limit(self, limit):
        # type: (int) -> None
        self.kelvin_limit = min(max(limit, MIN_KELVIN), MAX_KELVIN)

    @property
    def max_power(self):
        # type: () -> int
        "玩家设定的最大功率, 单位 RF/t; 未设定时为 0(不产热)。"
        return self._cached_max_power

    @max_power.setter
    def max_power(self, value):
        # type: (int) -> None
        self._cached_max_power = self.bdata[K_MAX_POWER] = value
        self.running_power = value * self.WORK_INTERVAL

    @property
    def kelvin_limit(self):
        # type: () -> int
        "玩家设定的最高温度, 单位 K; 未设定时为环境温度。"
        return self.bdata[K_KELVIN_LIMIT] or MIN_KELVIN

    @kelvin_limit.setter
    def kelvin_limit(self, value):
        # type: (int) -> None
        self.bdata[K_KELVIN_LIMIT] = value


@ElectricHeater.ForOperation(ElectricHeaterSubmitModifiesEvent)
def onSetModifies(event, machine):
    # type: (ElectricHeaterSubmitModifiesEvent, ElectricHeater) -> None
    if not isinstance(event.power, int) or not isinstance(event.kelvin_limit, int):
        return
    machine.set_power(event.power)
    machine.set_kelvin_limit(event.kelvin_limit)
