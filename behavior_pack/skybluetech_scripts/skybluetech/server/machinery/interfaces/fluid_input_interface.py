# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.method_weakref import ref_method
from ..basic import FluidContainer, GUIControl, RegisterMachine
from .base_interface import BaseInterface

if 0>1:
    import typing


@RegisterMachine
class FluidInputInterface(BaseInterface, FluidContainer, GUIControl):
    is_non_energy_machine = True
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_io_fix_mode = 0
    max_fluid_volume = 8000

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseInterface.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        GUIControl.__init__(self, dim, x, y, z, block_entity_data)
        self.on_fluid_slot_update_cb_ref = None

    def SetOnFluidSlotUpdateCallback(self, callback):
        # type: (typing.Callable[[], None]) -> None
        self.on_fluid_slot_update_cb_ref = ref_method(callback)

    def OnFluidSlotUpdate(self):
        if self.on_fluid_slot_update_cb_ref is not None:
            on_fluid_slot_update_cb = self.on_fluid_slot_update_cb_ref()
            if on_fluid_slot_update_cb is not None:
                on_fluid_slot_update_cb()
