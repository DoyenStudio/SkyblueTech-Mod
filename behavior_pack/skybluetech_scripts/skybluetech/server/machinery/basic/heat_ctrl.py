# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.facing import (
    FACING_DXYZ,
    OPPOSITE_FACING,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_HEAT_VALUE
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from .base_machine import BaseMachine


class HeatCtrl(BaseMachine):
    """
    热机机器类, 表示产热或吸热的机器。
    具有属性:
        - 热值(RF): 本机当前的绝对热值 H, 0K 对应 H = 0, 环境温度对应 H = 300
        - 开尔文值(K): 本机当前的开尔文温度值, 由热值换算

    热值与温度的换算用本机热容 `heat_capacity`(默认 `Thermal.HEAT_CAPACITY`), 即
    H = heat_capacity * T。热容只决定"移动这一段温度要搬多少热量", 不改变温度本身:
    热容越大, 升温降温越慢、也越费电。所以想让某一台机器"更重"时, 覆写这一个类属性
    即可, 其他机器完全不受影响。

    热力计算全部使用绝对热值, 并委托给 `phys_math.Thermal`, 本类不自带热力学公式:
        - 产热/吸热: `Thermal.HeatToTarget`(目标温度见 `heat_target_kelvin`)
        - 环境散热: `Thermal.ConductHeat`(环境视为无穷大热库, 牛顿冷却)
        - 热扩散: `Thermal.ConductHeat`

    需要: `__init__`

    类属性:
        spread_heat (bool): 是否扩散热量, 默认为 False
        max_heat_value (float): 本机相对环境温度的温升上限, 默认为 600.0
        env_conductance (float): 环境散热系数, 默认为 0.002
        electric_per_heat (float): 电→热单价, 默认取全局标准 `Thermal.ELECTRIC_PER_HEAT`

    覆写:
        - `OnTicking`
        - `OnHeatWork`
        - `heat_target_kelvin`
    """

    heat_power = 0
    "产热功率, 正值代表加热, 负值代表吸热"
    spread_heat = False
    "是否扩散热量"
    max_heat_value = 600
    "本机相对环境温度的温升上限, 单位 K"

    heat_capacity = Thermal.HEAT_CAPACITY
    """本机热容, 单位 RF/K, 默认等于全局的 `Thermal.HEAT_CAPACITY`。

    取默认值时热值与温度数值相同, 行为与过去完全一致。覆写成更大的值, 相当于给本机
    加了一大团需要加热/冷却的物质。注意各子类里以 RF/t 计的速率类常量(如产热功率、
    移热速率)同样会随热容放大, 需要一起检查, 否则温度变化速度会跟着变慢。
    """

    WORK_INTERVAL = 5
    "热力结算间隔, 单位 tick; 同时作为传热的 dt"

    env_conductance = 0.002
    """环境散热系数, 单位 RF/(tick*K)。

    环境视为无穷大热库, 按牛顿冷却律 Q = env_conductance * (T - T_env) * dt 双向换热。
    取 0.002 时, 1 RF/t(heat_power = 0.5) 的稳态温升约 50K, 与原三次方散热的表现一致。
    置 0 可关闭环境散热(机器将不再自动回落环境温度)。
    """

    electric_per_heat = Thermal.ELECTRIC_PER_HEAT
    """本机的电→热单价, 单位 RF电/RF热, 默认取全局标准 `Thermal.ELECTRIC_PER_HEAT`。

    电量与热量之间的换算一律走 `HeatFromElectric` / `ElectricCostOf`, 不要在子类里手写
    系数。覆写它可以只把这一台机器改得更省电或更费电(例如高效电热机)。
    """

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        heat_value = block_entity_data[K_HEAT_VALUE]
        # 缺省(新放置的机器)为环境温度
        if heat_value is None:
            heat_value = Thermal.STD_ENV_KELVIN
        # `K_HEAT_VALUE` 里存的是"参考热容下的热值": 默认热容是 1.0 RF/K, 所以它同时
        # 就是本机温度(K)。热容更大的机器也照样存温度, 好处是旧存档、客户端 UI 读数
        # 与其他机器读到的都是同一套数值, 不会因为改了热容而错位。
        self._heat_value = heat_value * self.heat_capacity
        self.t = 0
        self.neighbor_heaters = [None] * len(FACING_DXYZ)  # type: list[HeatCtrl | None]
        self._update_neighbor_heaters()

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        self.t += 1
        if self.t % self.WORK_INTERVAL == 0:
            self.t = 0
            self._heat_ctrl_work_once()

    def SetOutputHeatPower(self, power):
        # type: (float) -> None
        self.heat_power = power

    def OnHeatWork(self):
        # type: () -> None
        """
        热力结算前的回调, 每 `WORK_INTERVAL` tick 调用一次。

        子类可覆写以按本周期的实际耗能调整 `heat_power`(例如 `ElectricHeater`: 停机、到温、
        电量不足时置 0, 否则按 `electric_per_heat` 把设定功率换算成产热功率, 并按设定功率
        全额扣电)。本方法在产热/热扩散之前执行, 所以本周期设置的热功率本周期即生效。
        """

    def HeatFromElectric(self, rf):
        # type: (float) -> float
        "按本机单价把 RF 电换算成买得到的热量(RF)。"
        return Thermal.HeatFromElectric(rf, self.electric_per_heat)

    def ElectricCostOf(self, heat):
        # type: (float) -> float
        "按本机单价把热量(RF)换算成电费(RF)。"
        return Thermal.ElectricCostOfHeat(heat, self.electric_per_heat)

    def _heat_ctrl_work_once(self):
        self.OnHeatWork()
        self._update_heat_value()
        self._exchange_with_env()
        if self.spread_heat:
            self.share_heat()

    def _update_neighbor_heaters(self):
        from ..pool import GetMachineStrict

        for face, (dx, dy, dz) in enumerate(FACING_DXYZ):
            m = GetMachineStrict(self.dim, self.x + dx, self.y + dy, self.z + dz)
            if isinstance(m, HeatCtrl):
                self.neighbor_heaters[face] = m
                m.set_neighbor_heater(OPPOSITE_FACING[face], self)

    def set_neighbor_heater(self, face, m):
        # type: (int, HeatCtrl) -> None
        self.neighbor_heaters[face] = m

    def _update_heat_value(self):
        # type: () -> None
        """
        按 `heat_power` 产热/吸热。

        产热以 `heat_target_kelvin` 为目标温度, 吸热以绝对零度为下限, 由
        `Thermal.HeatToTarget` 以 `abs(heat_power)` 的速率限速逼近。
        """
        heat_power = self.heat_power if self.IsActive() else 0.0
        if not heat_power:
            return

        target_T = self.heat_target_kelvin if heat_power > 0 else 0.0
        res = Thermal.HeatToTarget(
            self.heat_value,
            target_T,
            max_power=abs(heat_power),
            capacity=self.heat_capacity,
        )
        self.heat_value = res.H_next

    def _exchange_with_env(self):
        # type: () -> None
        """
        与视为无穷大热库的环境做牛顿冷却。

        无论高于还是低于环境温度都会向环境温度靠拢, 所以机器断热后会自行回落到
        环境温度, 而不是把热量永远锁在自己身上。
        """
        env = Thermal.ENV_HEAT
        H = self.heat_value
        capacity = self.heat_capacity
        # 环境热值是按默认热容算的(ENV_HEAT 本身就等于环境温度), 所以判断"谁更热"
        # 必须比温度, 不能直接比热值: 热容大的机器热值天然更大。
        T = Thermal.GetKelvin(H, capacity)
        if T == Thermal.STD_ENV_KELVIN:
            return

        if T > Thermal.STD_ENV_KELVIN:
            res = Thermal.ConductHeat(
                H,
                env,
                conductance=self.env_conductance,
                dt=self.WORK_INTERVAL,
                capacity_hot=capacity,
            )
            H_next = res.H_hot_next
        else:
            res = Thermal.ConductHeat(
                env,
                H,
                conductance=self.env_conductance,
                dt=self.WORK_INTERVAL,
                capacity_cold=capacity,
            )
            H_next = res.H_cold_next

        if res.Q_transferred <= 0:
            return
        self.heat_value = H_next

    def share_heat(self):
        # type: () -> None
        """
        与相邻热机做纯热传导, 热量只从高温侧流向低温侧。

        每个邻居按 `Thermal.ConductHeat` 单独结算, 传热后的热值立即作为
        下一个邻居的起点, 保证本机不会把邻居"加热到超过自己"。
        """
        H = self.heat_value
        transferred = False
        for heater in self.neighbor_heaters:
            if heater is None:
                continue
            res = Thermal.ConductHeat(
                H,
                heater.heat_value,
                dt=self.WORK_INTERVAL,
                capacity_hot=self.heat_capacity,
                capacity_cold=heater.heat_capacity,
            )
            if res.Q_transferred <= 0:
                continue
            H = res.H_hot_next
            heater.heat_value = res.H_cold_next
            transferred = True
        if transferred:
            self.heat_value = H

    @property
    def heat_value(self):
        # type: () -> float
        "本机绝对热值, 单位 RF。"
        return self._heat_value

    @heat_value.setter
    def heat_value(self, value):
        self._heat_value = value
        # 落盘前换算成"参考热容下的热值", 见 __init__
        self.bdata[K_HEAT_VALUE] = value / self.heat_capacity

    @property
    def kelvin(self):
        # type: () -> float
        "本机温度, 单位 K。"
        return Thermal.GetKelvin(self.heat_value, self.heat_capacity)

    @property
    def max_kelvin(self):
        # type: () -> float
        "本机温度上限, 单位 K。"
        return Thermal.STD_ENV_KELVIN + self.max_heat_value

    @property
    def heat_target_kelvin(self):
        # type: () -> float
        """
        产热的目标温度, 单位 K, 默认为本机温度上限 `max_kelvin`。

        子类可覆写它来改变产热的目标(例如 `ElectricHeater` 用玩家设定的温度)。
        注意 `_update_heat_value` 会把单周期产热钳位在"距离目标还差多少"以内, 所以
        目标温度不能设得低于本机当前温度, 否则本周期直接不产热。
        """
        return self.max_kelvin
