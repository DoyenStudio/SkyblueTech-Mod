# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from ..define import flags
from ..machinery_def.battery_cube import *
from ..ui_sync.machinery.battery_cube import BatteryCubeUISync
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine

INFINITY = float("inf")


@RegisterMachine
class BatteryCube(BaseMachine, GUIControl, ItemContainer):
    block_name = "skybluetech:battery_cube"
    store_rf_max = 100000
    is_container = False
    energy_io_mode = (1, 1, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = BatteryCubeUISync.NewServer(self).Activate()
        self.power = 0
        self.delay = 20

    def OnTicking(self):
        if self.IsActive():
            last_power = self.store_rf
            now_power = self.store_rf = self.addPowerIntoWireNetwork(self.store_rf)
            if now_power == last_power:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
            if now_power == 0:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
        res = BaseMachine.AddPower(self, rf, is_generator, max_limit, depth)
        if self.store_rf > 0 and self.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        return res

    def OnTryActivate(self):
        # type: () -> None
        self.ResetDeactiveFlags()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        self.updateStoreRF()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return BATTERY_TAG in item.GetBasicInfo().tags

    def updateStoreRF(self):
        srf = 0
        for slot in range(self.GetSlotSize()):
            item = self.GetSlotItem(slot)
            if item is None:
                continue
            srf += BATTERY_STORE_RF.get(item.newItemName, 0)
        self.store_rf_max = srf
        if self.store_rf > srf:
            self.store_rf = srf

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)