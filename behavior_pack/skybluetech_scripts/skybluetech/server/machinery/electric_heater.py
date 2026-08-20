# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.ELECTRIC_HEATER
from ...common.events.machinery.electric_heater import ElectricHeaterSubmitModifiesEvent
from ...common.machinery_def.electric_heater import (
    K_KELVIN_LIMIT,
    K_SET_POWER,
    STORE_RF_MAX,
)
from .basic import (
    GUIControl,
    HeatCtrl,
    OperationListener,
    PowerControl,
    RegisterMachine,
)

MAX_POWER = STORE_RF_MAX


@RegisterMachine
class ElectricHeater(HeatCtrl, GUIControl, PowerControl, OperationListener):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    max_heat_value = 500
    spread_heat = True

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._cached_running_power = self.bdata[K_SET_POWER] or 0
        self._update_heat_power()
        self.t = 0

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        self.t += 1
        if self.t % 5 == 0 and self.IsActive():
            if self.kelvin <= self.kelvin_limit:
                if self.PowerEnough():
                    self.ReducePower()
                self._update_heat_power()
            else:
                self.SetOutputHeatPower(0)

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def set_power(self, power):
        # type: (int) -> None
        self.running_power = min(MAX_POWER, power) * 5  # 5 tick 运行一次
        self._update_heat_power()

    def set_kelvin_limit(self, limit):
        # type: (int) -> None
        self.kelvin_limit = limit

    def _update_heat_power(self):
        self.SetOutputHeatPower(self.running_power * 0.1)

    @property
    def running_power(self):
        # type: () -> int
        return self._cached_running_power

    @running_power.setter
    def running_power(self, value):
        # type: (int) -> None
        self._cached_running_power = self.bdata[K_SET_POWER] = value

    @property
    def kelvin_limit(self):
        # type: () -> int
        return self.bdata[K_KELVIN_LIMIT] or 400

    @kelvin_limit.setter
    def kelvin_limit(self, value):
        # type: (int) -> None
        self.bdata[K_KELVIN_LIMIT] = value


@ElectricHeater.ForOperation(ElectricHeaterSubmitModifiesEvent)
def onSetPower(event, machine):
    # type: (ElectricHeaterSubmitModifiesEvent, ElectricHeater) -> None
    if not isinstance(event.power, int) or not isinstance(event.kelvin_limit, int):
        return
    machine.set_power(event.power)
    machine.set_kelvin_limit(event.kelvin_limit)
