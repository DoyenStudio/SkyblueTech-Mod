# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from ..define import flags
from ..machinery_def.battery_cube import *
from ..ui_sync.machines.battery_cube import BatteryCubeUISync
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict

K_MODE = "mode"
K_BOUND_BLOCK_POS = "bound_block_pos"

MODE_SENDER = 0
MODE_RECEIVER = 1


@RegisterMachine
class WirelessRFTransporter(BaseMachine, GUIControl, ItemContainer):
    block_name = "skybluetech:wireless_rf_transporter"
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

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
        # type: (int, bool, int | None, int) -> tuple[bool, int]
        if self.mode == MODE_SENDER:
            if not is_generator:
                mPos = self.bound_block_pos
                if not isinstance(mPos, list):
                    return BaseMachine.AddPower(self, rf, is_generator, max_limit, depth)
                else:
                    dim, x, y, z = mPos
                    m = GetMachineStrict(dim, x, y, z)
                    if m is None:
                        return BaseMachine.AddPower(self, rf, is_generator, max_limit, depth)
                    return m.AddPower(rf, is_generator=True, depth=depth+1)
            else:
                # 不应该出现这种情况, 即为发送器模式但是接收充能
                return False, rf
        elif self.mode == MODE_RECEIVER:
            if is_generator:
                return BaseMachine.AddPower(self, rf, True, max_limit, depth)
            else:
                # 电网中受电, 忽略
                return False, rf
        else:
            return False, rf

        
