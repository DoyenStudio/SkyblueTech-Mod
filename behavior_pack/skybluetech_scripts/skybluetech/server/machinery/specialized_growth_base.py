# coding=utf-8
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ...common.define.id_enum import Machinery
from ...common.machinery_def.specialized_growth_base import FLUID_SLOT_MAX_VOLUMES
from .basic import GUIControl, MultiFluidContainer
from .basic.upgrade_control import ItemUpgradeControl
from .core import RegisterMachine
from .core.pool import GetLoadedMachine


@RegisterMachine
class SpecializedGrowthBase(GUIControl, MultiFluidContainer, ItemUpgradeControl):
    block_name = Machinery.SPECIALIZED_GROWTH_BASE
    is_non_energy_machine = True
    item_input_slots = (0,)
    item_output_slots = (1, 2, 3, 4)
    upgrade_slot_start = 5
    fluid_input_slots = (0,)
    fluid_output_slots = (1,)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = -1

    def __init__(self, dim, x, y, z, block_entity_data):
        super(SpecializedGrowthBase, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnSlotUpdate(self._on_slot_update)
        self.handler.SubscribeOnFluidSlotUpdate(self._on_fluid_update)
        self.handler.SubscribeOnInvalidateCaches(self._notify_chamber)
        # LoadMachine 在构造结束后才登记本实例；覆盖两种上下加载顺序。
        ExecLater(0, self._notify_chamber)

    def _on_slot_update(self, slot):
        self._notify_chamber()

    def _on_fluid_update(self, slot, is_final):
        if is_final:
            self._notify_chamber()

    def _notify_chamber(self):
        from .specialized_growth_chamber import SpecializedGrowthChamber

        if GetLoadedMachine(self.dim, *self.xyz) is not self:
            return
        chamber = GetLoadedMachine(self.dim, self.x, self.y + 1, self.z)
        if isinstance(chamber, SpecializedGrowthChamber):
            chamber.RequestBaseExchange()
