# coding=utf-8
from .base_machine import BaseMachine
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define.facing import (
    FACING_DXYZ,
    OPPOSITE_FACING,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_HEAT_VALUE,
    ENV_TEMPERATURE,
)


class HeatCtrl(BaseMachine):
    """
    热机机器类, 表示产热或吸热的机器。
    具有属性:
        - 热值(R/W): 本机当前的热量值
        - 开尔文值(R): 本机当前的开尔文温度值

    需要: `__init__`

    类属性:
        spread_heat (bool): 是否扩散热量, 默认为 False
        max_heat_value (float): 本机最大热值, 默认为 600.0

    覆写:
        `OnTicking`
    """

    heat_power = 0
    "产热功率, 正值代表高于环境温度, 负值代表低于环境温度"
    spread_heat = False
    "是否扩散热量"
    max_heat_value = 600
    "本机最大热值"

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._heat_value = block_entity_data[K_HEAT_VALUE] or 0
        self.t = 0
        self.one_div_a = self.max_heat_value**2  # **3
        self.neighbor_heaters = [None] * len(FACING_DXYZ)  # type: list[HeatCtrl | None]
        self._update_neighbor_heaters()

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        self.t += 1
        if self.t % 5 == 0:
            self.t = 0
            self._heat_ctrl_work_once()

    def SetOutputHeatPower(self, power):
        # type: (float) -> None
        self.heat_power = power

    def _heat_ctrl_work_once(self):
        self._update_heat_value()
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
        if self.IsActive():
            new_heat_value = self.heat_value + self.heat_power
        else:
            new_heat_value = self.heat_value
        self.heat_value = new_heat_value - self.calcuate_heat_loss(new_heat_value)

    def calcuate_heat_loss(self, heat_value):
        # type: (float) -> float
        chk = heat_value / self.one_div_a
        if chk > 1 if chk > 0 else chk < -1:
            return heat_value
        val = heat_value**3 / self.one_div_a
        return min(val, heat_value) if val > 0 else max(val, heat_value)

    def share_heat(self):
        heaters = [
            h
            for h in self.neighbor_heaters
            if h is not None and h.heat_value < self.heat_value
        ]
        if not heaters:
            return

        m = self.heat_value
        ratio = 0.4

        heats = [h.heat_value for h in heaters]
        demands = [ratio * (m - h) for h in heats]
        D = sum(demands)
        if D <= 0:
            return

        s = min(1.0, m / D)

        total = 0.0
        for i, heater in enumerate(heaters):
            actual = demands[i] * s
            heater.heat_value = heater.heat_value + actual
            total += actual
        self.heat_value = self.heat_value - total

    @property
    def heat_value(self):
        # type: () -> float
        return self._heat_value

    @heat_value.setter
    def heat_value(self, value):
        self._heat_value = value
        self.bdata[K_HEAT_VALUE] = value

    @property
    def kelvin(self):
        return self.heat_value + ENV_TEMPERATURE
