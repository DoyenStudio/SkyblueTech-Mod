# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ..basic import ItemContainer, RegisterMachine
from .base_interface import BaseInterface

if 0:
    from typing import Callable


@RegisterMachine
class ItemOutputInterface(BaseInterface, ItemContainer):
    is_non_energy_machine = True
    input_slots = ()
    output_slots = (0, 1, 2, 3, 4)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseInterface.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)

    def SetOnSlotUpdateCallback(self, callback):
        # type: (Callable[[int], None]) -> None
        self.on_slot_update_cb_ref = ref(callback)

    def OnSlotUpdate(self, slot_pos):
        if self.on_slot_update_cb_ref is not None:
            on_slot_update_cb = self.on_slot_update_cb_ref()
            if on_slot_update_cb is not None:
                on_slot_update_cb(slot_pos)
