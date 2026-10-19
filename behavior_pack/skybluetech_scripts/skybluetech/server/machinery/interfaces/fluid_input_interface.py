# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import MultiFluidContainer, GUIControl
from ..core import RegisterMachine
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_interface import FLUID_INTERFACE_MAX_VOLUME
from .base_interface import BaseInterface

if 0>1:
    import typing


@RegisterMachine
class FluidInputInterface(GUIControl, MultiFluidContainer, BaseInterface):
    is_non_energy_machine = True
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (FLUID_INTERFACE_MAX_VOLUME,)
    fluid_input_slots = {0}
    fluid_output_slots = set()
    migrate_legacy_fluid_data = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidInputInterface, self).__init__(dim, x, y, z, block_entity_data)
        self.on_fluid_slot_update_cb_ref = None
        self.handler.SubscribeOnFluidSlotUpdate(self._fluid_input_interface_on_fluid_slot_update)

    def SetOnFluidSlotUpdateCallback(self, callback):
        # type: (typing.Callable[[], None]) -> None
        self.on_fluid_slot_update_cb_ref = ref_method(callback)

    def _fluid_input_interface_on_fluid_slot_update(self, slot, is_final):
        if is_final and self.on_fluid_slot_update_cb_ref is not None:
            on_fluid_slot_update_cb = self.on_fluid_slot_update_cb_ref()
            if on_fluid_slot_update_cb is not None:
                on_fluid_slot_update_cb()
