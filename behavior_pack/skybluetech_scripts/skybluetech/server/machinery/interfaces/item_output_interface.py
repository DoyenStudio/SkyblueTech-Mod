# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import ItemContainer
from ..core import RegisterMachine
from .base_interface import BaseInterface

if 0>1:
    import typing


@RegisterMachine
class ItemOutputInterface(ItemContainer, BaseInterface):
    is_non_energy_machine = True
    item_input_slots = ()
    item_output_slots = (0, 1, 2, 3, 4)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ItemOutputInterface, self).__init__(dim, x, y, z, block_entity_data)
        self.on_slot_update_cb_ref = None
        self.handler.SubscribeOnSlotUpdate(self._item_output_interface_on_slot_update)

    def SetOnSlotUpdateCallback(self, callback):
        # type: (typing.Callable[[int], None]) -> None
        self.on_slot_update_cb_ref = ref_method(callback)

    def _item_output_interface_on_slot_update(self, slot_pos):
        if self.on_slot_update_cb_ref is not None:
            on_slot_update_cb = self.on_slot_update_cb_ref()
            if on_slot_update_cb is not None:
                on_slot_update_cb(slot_pos)
