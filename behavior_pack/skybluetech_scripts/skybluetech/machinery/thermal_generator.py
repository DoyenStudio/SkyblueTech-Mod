# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from ..define import flags
from ..define.id_enum.machinery import THERMAL_GENERATOR as MACHINE_ID
from ..machinery_def.thermal_generator import TICK_POWER
from ..ui_sync.machines.thermal_generator import ThermalGeneratorUISync
from .basic import AutoSaver, BaseMachine, ItemContainer, GUIControl, WorkRenderer, RegisterMachine

K_BURN_SEC_LEFT = "burn_sec_left"
K_MAX_BURN_SEC = "max_burn_secs"
K_ACTIVE = "active"

SecondsPerTick = 0.05


@RegisterMachine
class ThermalGenerator(AutoSaver, ItemContainer, GUIControl, WorkRenderer):
    block_name = MACHINE_ID
    store_rf_max = 14400
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    input_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ThermalGeneratorUISync.NewServer(self).Activate()
        self.OnSync()

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    def OnTicking(self):
        if self.IsActive():
            if self.burn_seconds_left <= 0:
                self.is_burning = self.next_burn()
                return
            self.burn_seconds_left -= SecondsPerTick
            self.AddPower(TICK_POWER, True)
            self.OnSync()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return not (item.GetBasicInfo().fuelDuration <= 0 or item.newItemName == "minecraft:lava_bucket")

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.power = TICK_POWER if self.burn_seconds_left > 0 else 0
        self.sync.rest_burn_relative = float(self.burn_seconds_left) / self.max_burn_seconds
        self.sync.MarkedAsChanged()

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        data = self.bdata
        self.burn_seconds_left = data[K_BURN_SEC_LEFT] or 0
        self.max_burn_seconds = data[K_MAX_BURN_SEC] or 1
        self.is_burning = self.burn_seconds_left > 0

    def Dump(self):
        BaseMachine.Dump(self)
        self.bdata[K_BURN_SEC_LEFT] = self.burn_seconds_left
        self.bdata[K_MAX_BURN_SEC] = self.max_burn_seconds

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.store_rf < self.store_rf_max and self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            self.next_burn()

    def OnTryActivate(self):
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL):
            _, self.store_rf = self.AddPower(self.store_rf, True)
            if self.store_rf < self.store_rf_max:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BaseMachine.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def next_burn(self):
        if self.store_rf >= self.store_rf_max:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
            return False
        mainSlotItem = self.GetSlotItem(0)
        if mainSlotItem is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            self.is_burning = False
            return False
        burnTime = mainSlotItem.GetBasicInfo().fuelDuration
        self.burn_seconds_left = burnTime
        self.max_burn_seconds = burnTime
        mainSlotItem.count -= 1
        self.SetSlotItem(0, mainSlotItem)
        self.is_burning = True
        return True
