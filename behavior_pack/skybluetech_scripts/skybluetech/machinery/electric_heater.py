# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.timer import Delay
from ..define.id_enum.machinery import ELECTRIC_HEATER as MACHINE_ID
from ..define.events.machinery.electric_heater import ElectricHeaterSetPowerEvent
from ..ui_sync.machinery.electric_heater import ElectricHeaterUISync
from ..utils.action_commit import SafeGetMachine
from .basic import AutoSaver, HeatCtrl, GUIControl, PowerControl, RegisterMachine
from .pool import GetMachineStrict

K_SET_POWER = "set_power"
MAX_POWER = 1 << 32


@RegisterMachine
class ElectricHeater(AutoSaver, HeatCtrl, GUIControl, PowerControl):
    block_name = MACHINE_ID
    store_rf_max = 64000

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        HeatCtrl.__init__(self, dim, x, y, z, block_entity_data)
        PowerControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ElectricHeaterUISync.NewServer(self).Activate()
        self.inited = False

    def OnLoad(self):
        # type: () -> None
        PowerControl.OnLoad(self)
        HeatCtrl.OnLoad(self)
        self.running_power = self.bdata[K_SET_POWER] or 0
        self.initLater()

    def OnNeighborChanged(self, evt):
        self.updateHeatersNearby()

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
        self.OnSync()

    def OnSync(self):
        self.sync.rf_max = self.store_rf_max
        self.sync.storage_rf = self.store_rf
        self.sync.power = self.running_power
        self.sync.current_temperature = self.kelvin
        self.sync.MarkedAsChanged()

    def Dump(self):
        PowerControl.Dump(self)
        HeatCtrl.Dump(self)
        self.bdata[K_SET_POWER] = self.running_power

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        PowerControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def gen_heat(self):
        if self.PowerEnough():
            self.ReducePower()
            self.kelvin = float(self.running_power) / self.heat_c * 100 + self.kelvin

    @Delay(0)
    def initLater(self):
        self.updateHeatersNearby()
        self.inited = True
        self.OnSync()

    def updateHeatersNearby(self):
        self.machines = [] # type: list[HeatCtrl]
        for dx, dy, dz in (
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (0, 0, -1)
        ):
            m = GetMachineStrict(self.dim, self.x + dx, self.y + dy, self.z + dz)
            if isinstance(m, HeatCtrl):
                self.machines.append(m)

    def setPower(self, power):
        # type: (int) -> None
        self.running_power = min(MAX_POWER, power)


@ElectricHeaterSetPowerEvent.Listen()
def onSetPower(event):
    # type: (ElectricHeaterSetPowerEvent) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, ElectricHeater):
        return
    if not isinstance(event.power, int):
        return
    m.setPower(event.power)

