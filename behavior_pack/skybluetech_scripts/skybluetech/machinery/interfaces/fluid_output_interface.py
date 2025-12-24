# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ...ui_sync.machines.fluid_interface import FluidInterfaceUISync
from ..basic import BaseMachine, FluidContainer, GUIControl, RegisterMachine

# LOADED_INTERFACES
from ...machinery_def import (
    fermenter
)
#

REG_BLOCK_IDS = (
    fermenter.IO_FLUID2,
    fermenter.IO_GAS,
)


@RegisterMachine
class FluidOutputInterface(BaseMachine, FluidContainer, GUIControl):
    extra_block_names = REG_BLOCK_IDS
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_io_fix_mode = 0
    max_fluid_volume = 8000

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = FluidInterfaceUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    def Dump(self):
        BaseMachine.Dump(self)
        FluidContainer.Dump(self)
