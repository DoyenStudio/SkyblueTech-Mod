# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import MultiFluidContainer, GUIControl
from ..core import RegisterMachine
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_interface import FLUID_INTERFACE_MAX_VOLUME
from .base_interface import BaseInterface

if 0>1:
    import typing


@RegisterMachine
class FluidOutputInterface(GUIControl, MultiFluidContainer, BaseInterface):
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (FLUID_INTERFACE_MAX_VOLUME,)
    fluid_input_slots = set()
    fluid_output_slots = {0}
    player_fluid_input_slots = {0}
    migrate_legacy_fluid_data = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidOutputInterface, self).__init__(dim, x, y, z, block_entity_data)
        self.on_fluid_slot_update_cb_ref = None
        self.on_added_fluid_cb_ref = None
        self.on_reduced_fluid_cb_ref = None
        self.handler.SubscribeOnFluidSlotUpdate(self._fluid_output_interface_on_fluid_slot_update)
        self.handler.SubscribeOnAddedFluid(self._fluid_output_interface_on_added_fluid)
        self.handler.SubscribeOnReducedFluid(self._fluid_output_interface_on_reduced_fluid)

    def SetOnFluidSlotUpdateCallback(self, callback):
        # type: (typing.Callable[[], None]) -> None
        self.on_fluid_slot_update_cb_ref = ref_method(callback)

    def SetOnAddedFluidCallback(self, callback):
        # type: (typing.Callable[[str, float], None]) -> None
        self.on_added_fluid_cb_ref = ref_method(callback)

    def SetOnReducedFluidCallback(self, callback):
        # type: (typing.Callable[[str, float], None]) -> None
        self.on_reduced_fluid_cb_ref = ref_method(callback)

    def _fluid_output_interface_on_fluid_slot_update(self, slot, is_final):
        if is_final and self.on_fluid_slot_update_cb_ref is not None:
            on_fluid_slot_update_cb = self.on_fluid_slot_update_cb_ref()
            if on_fluid_slot_update_cb is not None:
                on_fluid_slot_update_cb()

    def _fluid_output_interface_on_added_fluid(self, slot, fluid_id, added_fluid_volume, is_final):
        if self.on_added_fluid_cb_ref is not None:
            on_added_fluid_cb = self.on_added_fluid_cb_ref()
            if on_added_fluid_cb is not None:
                on_added_fluid_cb(fluid_id, added_fluid_volume)

    def _fluid_output_interface_on_reduced_fluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        if self.on_reduced_fluid_cb_ref is not None:
            on_reduced_fluid_cb = self.on_reduced_fluid_cb_ref()
            if on_reduced_fluid_cb is not None:
                on_reduced_fluid_cb(fluid_id, reduced_fluid_volume)
