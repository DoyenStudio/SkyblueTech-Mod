# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from ..define import flags
from ..define.id_enum.machinery import WIRELESS_RF_TRANSPORTER as MACHINE_ID
from ..machinery_def.battery_cube import *
from ..ui_sync.machinery.battery_cube import BatteryCubeUISync
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict

K_MODE = "mode"
K_BOUND_BLOCK_POS = "bound_block_pos"

MODE_SENDER = 0
MODE_RECEIVER = 1


@RegisterMachine
class WirelessRFTransporter(BaseMachine, GUIControl, ItemContainer):
    block_name = MACHINE_ID
    store_rf_max = 100000
    energy_io_mode = (1, 1, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)

    def OnLoad(self):
        self.mode = self.bdata[K_MODE] or MODE_SENDER
        self.bound_block_pos = self.bdata[K_BOUND_BLOCK_POS] or False # type: list[int] | bool

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    def Dump(self):
        self.bdata[K_MODE] = self.mode
        self.bdata[K_BOUND_BLOCK_POS] = self.bound_block_pos

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        pass

        
