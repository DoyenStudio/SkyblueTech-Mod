# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import ELECTRIC_HEATER as MACHINE_ID
from ...common.events.machinery.electric_heater import ElectricHeaterSetPowerEvent
from ...common.ui_sync.machinery.electric_heater import ElectricHeaterUISync
from .utils.action_commit import SafeGetMachine
from .basic import HeatCtrl, GUIControl, PowerControl, RegisterMachine
from .pool import GetMachineStrict

K_SET_POWER = "set_power"
MAX_POWER = 1 << 32


@RegisterMachine
class ElectricHeater(HeatCtrl, GUIControl, PowerControl):
    block_name = MACHINE_ID
    store_rf_max = 64000

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = ElectricHeaterUISync.NewServer(self).Activate()
        self.inited = False
        self._cached_running_power = self.bdata[K_SET_POWER] or 0
        self._init_later()

    def OnNeighborChanged(self, evt):
        self.update_heaters_nearby()

    def OnTicking(self):
        if not self.inited:
            return
        HeatCtrl.OnTicking(self)
        if self.IsActive():
            if self.PowerEnough():
                self.ReducePower()
                self.gen_heat()
        for m in self.machines:
            self.ShareHeat(m)
        self.CallSync()

    def OnSync(self):
        self.sync.rf_max = self.store_rf_max
        self.sync.storage_rf = self.store_rf
        self.sync.power = self.running_power
        self.sync.current_temperature = self.kelvin
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def gen_heat(self):
        if self.PowerEnough():
            self.ReducePower()
            self.kelvin = float(self.running_power) / self.heat_c * 100 + self.kelvin

    @Delay(0)
    def _init_later(self):
        self.update_heaters_nearby()
        self.inited = True
        self.CallSync()

    def update_heaters_nearby(self):
        self.machines = []  # type: list[HeatCtrl]
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)):
            m = GetMachineStrict(self.dim, self.x + dx, self.y + dy, self.z + dz)
            if isinstance(m, HeatCtrl):
                self.machines.append(m)

    def set_power(self, power):
        # type: (int) -> None
        self.running_power = min(MAX_POWER, power)

    @property
    def running_power(self):
        # type: () -> int
        return self._cached_running_power

    @running_power.setter
    def running_power(self, value):
        # type: (int) -> None
        self._cached_running_power = self.bdata[K_SET_POWER] = value


@ElectricHeaterSetPowerEvent.Listen()
def onSetPower(event):
    # type: (ElectricHeaterSetPowerEvent) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, ElectricHeater):
        return
    if not isinstance(event.power, int):
        return
    m.set_power(event.power)
