# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ....common.ui_sync.machinery.fluid_interface import FluidInterfaceUISync
from ..basic import BaseMachine, FluidContainer, GUIControl, RegisterMachine

if 0:
    from typing import Callable

# LOADED_INTERFACES
from ....common.machinery_def import fermenter
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
        self.on_fluid_slot_update_cb_ref = None

    def OnTicking(self):
        FluidContainer.OnTicking(self)

    def OnSync(self):
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    def SetOnFluidSlotUpdateCallback(self, callback):
        # type: (Callable[[], None]) -> None
        self.on_fluid_slot_update_cb_ref = ref(callback)

    def OnFluidSlotUpdate(self):
        if self.on_fluid_slot_update_cb_ref is not None:
            on_fluid_slot_update_cb = self.on_fluid_slot_update_cb_ref()
            if on_fluid_slot_update_cb is not None:
                on_fluid_slot_update_cb()
