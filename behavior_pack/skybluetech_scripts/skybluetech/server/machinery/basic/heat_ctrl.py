# coding=utf-8
from .base_machine import BaseMachine
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define.fluids.fluid_c import fluid_c_values

K_KELVIN = "kelvin"
ENV_TEMPERATURE = 300.0
S = 0.01
D = 0.001
TICK_TIME = 20
DIFF_THRESOLD = 1e-3
SELF_M = 10


class HeatCtrl(BaseMachine):
    """
    热机机器类, 表示产热或吸热的机器。

    需要: `__init__`

    类属性:
        heat_loss (float): 热量流失值, 默认为 1.0
        original_heat_c (float): 原始比热容, 默认为 4000.0

    覆写:
        `OnLoad`
        `OnTicking`
        `Dump`
    """

    heat_loss = 1
    "热量散失值, 越大表示散热越快。"
    original_heat_c = 4000
    "原始比热容"
    # auto_share_heat = True
    # "是否自动传递热量"

    def __init__(self, dim, x, y, z, block_entity_data):
        self.heat_c = self.original_heat_c

    def OnTicking(self):
        self._heat_loss()

    def ShareHeat(self, other):
        # type: (HeatCtrl) -> bool
        """
        分享、传递热量给给定的机器， 机器必须继承 `HeatCtrl` 类。

        Args:
            other (HeatCtrl): 对应机器

        Returns:
            bool: 是否进行了传热, 如果温度差异过小则不会传热
        """
        diff = abs(self.kelvin - other.kelvin)
        if diff <= DIFF_THRESOLD:
            return False
        R_self = D / self.heat_c
        R_other = D / other.heat_c
        heat_flux = diff / (R_self + R_other) * S
        dQ = heat_flux / TICK_TIME
        if self.kelvin > other.kelvin:
            self.kelvin -= dQ / self.heat_c
            other.kelvin += dQ / other.heat_c
        else:
            self.kelvin += dQ / self.heat_c
            other.kelvin -= dQ / other.heat_c
        return True

    def _heat_loss(self):
        k = self.kelvin
        if k > ENV_TEMPERATURE:
            self.kelvin = max(
                ENV_TEMPERATURE,
                k - (k**4 - ENV_TEMPERATURE**4) * self.heat_loss * 1e-10,
            )
        # print "val", (self.kelvin**4 - ENV_TEMPERATURE**4) * self.heat_loss * 1e-10

    def InputFluidAndUpdateHeat(self, fluid_id, prev_fluid_volume, new_fluid_volume):
        # type: (str, float, float) -> None
        """
        当机器接受了具有比热容的流体时调用。
        会更新此机器温度。

        Args:
            fluid_id (str): 流体类型
            new_volume (float): 当前此流体的体积
        """
        add_fluid_volume = new_fluid_volume - prev_fluid_volume
        orig_q = self.kelvin * self.heat_c * (prev_fluid_volume + SELF_M)
        self.FlushCValueByFluid(fluid_id, add_fluid_volume, new_fluid_volume)
        self.kelvin = (
            (orig_q + fluid_c_values[fluid_id] * ENV_TEMPERATURE * add_fluid_volume)
            / self.heat_c
            / (new_fluid_volume + SELF_M)
        )
        # print "fluid_c:", fluid_c_values[fluid_id], "my_c:", self.heat_c, "k:", self.kelvin

    def FlushCValueByFluid(self, fluid_id, add_volume, new_volume):
        # type: (str | None, float, float) -> None
        """
        根据所给流体类型和体积更新此机器的比热容。

        Args:
            fluid_id (str): 流体种类
            fluid_volume (float): 添加的此流体的体积
        """
        if fluid_id is None or new_volume == 0:
            self.heat_c = self.original_heat_c
        else:
            fluid_c = fluid_c_values[fluid_id]
            self.heat_c = self.original_heat_c * (
                float(SELF_M) / (new_volume + SELF_M)
            ) + fluid_c * (float(new_volume) / (new_volume + SELF_M))

    @property
    def kelvin(self):
        # type: () -> float
        return self.bdata[K_KELVIN] or ENV_TEMPERATURE

    @kelvin.setter
    def kelvin(self, value):
        # type: (float) -> None
        self.bdata[K_KELVIN] = value
