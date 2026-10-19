# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import FluidContainer, GUIControl
from ..core import RegisterMachine
from .base_interface import BaseInterface

if 0>1:
    import typing


@RegisterMachine
class FluidOutputInterface(GUIControl, FluidContainer, BaseInterface):
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_io_fix_mode = 0
    max_fluid_volume = 8000

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidOutputInterface, self).__init__(dim, x, y, z, block_entity_data)
        self.on_fluid_slot_update_cb_ref = None
        self.on_added_fluid_cb_ref = None
        self.on_reduced_fluid_cb_ref = None
        self.handler.SubscribeOnSingleFluidSlotUpdate(self._fluid_output_interface_on_fluid_slot_update)
        self.handler.SubscribeOnSingleAddedFluid(self._fluid_output_interface_on_added_fluid)
        self.handler.SubscribeOnSingleReducedFluid(self._fluid_output_interface_on_reduced_fluid)

    def SetOnFluidSlotUpdateCallback(self, callback):
        # type: (typing.Callable[[], None]) -> None
        self.on_fluid_slot_update_cb_ref = ref_method(callback)

    def SetOnAddedFluidCallback(self, callback):
        # type: (typing.Callable[[str, float], None]) -> None
        self.on_added_fluid_cb_ref = ref_method(callback)

    def SetOnReducedFluidCallback(self, callback):
        # type: (typing.Callable[[str, float], None]) -> None
        self.on_reduced_fluid_cb_ref = ref_method(callback)

    def _fluid_output_interface_on_fluid_slot_update(self):
        if self.on_fluid_slot_update_cb_ref is not None:
            on_fluid_slot_update_cb = self.on_fluid_slot_update_cb_ref()
            if on_fluid_slot_update_cb is not None:
                on_fluid_slot_update_cb()

    def _fluid_output_interface_on_added_fluid(self, fluid_id, added_fluid_volume):
        if self.on_added_fluid_cb_ref is not None:
            on_added_fluid_cb = self.on_added_fluid_cb_ref()
            if on_added_fluid_cb is not None:
                on_added_fluid_cb(fluid_id, added_fluid_volume)

    def _fluid_output_interface_on_reduced_fluid(self, fluid_id, reduced_fluid_volume):
        if self.on_reduced_fluid_cb_ref is not None:
            on_reduced_fluid_cb = self.on_reduced_fluid_cb_ref()
            if on_reduced_fluid_cb is not None:
                on_reduced_fluid_cb(fluid_id, reduced_fluid_volume)
