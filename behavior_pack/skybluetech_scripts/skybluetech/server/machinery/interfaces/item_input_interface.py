# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import ItemContainer, RegisterMachine
from .base_interface import BaseInterface

if 0:
    from typing import Callable


@RegisterMachine
class ItemInputInterface(BaseInterface, ItemContainer):
    is_non_energy_machine = True
    input_slots = (0, 1, 2, 3, 4)
    output_slots = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseInterface.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.on_slot_update_cb_ref = None

    def SetOnSlotUpdateCallback(self, callback):
        # type: (Callable[[int], None]) -> None
        self.on_slot_update_cb_ref = ref_method(callback)

    def OnSlotUpdate(self, slot_pos):
        if self.on_slot_update_cb_ref is not None:
            on_slot_update_cb = self.on_slot_update_cb_ref()
            if on_slot_update_cb is not None:
                on_slot_update_cb(slot_pos)
