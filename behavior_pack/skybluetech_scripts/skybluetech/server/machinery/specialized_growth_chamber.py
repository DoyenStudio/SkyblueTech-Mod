# coding=utf-8
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ...common.define.id_enum import Machinery
from ...common.machinery_def.specialized_growth_chamber import (
    FLUID_SLOT_MAX_VOLUMES,
    POWER_COST,
    STORE_RF_MAX,
    recipes,
)
from .basic import MultiFluidContainer, Processor
from .basic.slot_reads import accepts_slot_reads
from .core import RegisterMachine
from .core.pool import GetLoadedMachine
from .utils.specialized_growth_exchange import move_fluid, move_item


@RegisterMachine
class SpecializedGrowthChamber(Processor, MultiFluidContainer):
    block_name = Machinery.SPECIALIZED_GROWTH_CHAMBER
    recipes = recipes
    running_power = POWER_COST
    store_rf_max = STORE_RF_MAX
    process_item = True
    process_fluid = True
    item_input_slots = (0, 1, 2)
    item_output_slots = (3,)
    item_input_slots_by_face = {}
    item_output_slots_by_face = {}
    fluid_input_slots = (0,)
    fluid_output_slots = (1,)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots_by_face = {}
    fluid_output_slots_by_face = {}
    upgrade_slot_start = 4
    upgrade_slots = 0
    allow_upgraders = frozenset()

    def __init__(self, dim, x, y, z, block_entity_data):
        self._exchange_running = False
        self._exchange_pending = False
        super(SpecializedGrowthChamber, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnSlotUpdate(self._on_exchange_slot_update)
        self.handler.SubscribeOnFluidSlotUpdate(self._on_exchange_fluid_update)
        self.handler.SubscribeOnInvalidateCaches(self.RequestBaseExchange)
        self.handler.SubscribeOnUnload(self._on_exchange_unload)
        self.RequestBaseExchange()

    def _on_exchange_slot_update(self, slot):
        self.RequestBaseExchange()

    def _on_exchange_fluid_update(self, slot, is_final):
        if is_final:
            self.RequestBaseExchange()

    def _on_exchange_unload(self):
        self._exchange_pending = False

    def RequestBaseExchange(self):
        if self._exchange_running or self._exchange_pending:
            return
        self._exchange_pending = True
        ExecLater(0, self._flush_base_exchange)

    def _flush_base_exchange(self):
        if self._exchange_pending:
            self.ExchangeWithBase()

    def ExchangeWithBase(self):
        from .specialized_growth_base import SpecializedGrowthBase

        if self._exchange_running:
            return
        if self._applying_recipe:
            self.RequestBaseExchange()
            return
        self._exchange_pending = False
        if GetLoadedMachine(self.dim, *self.xyz) is not self:
            return
        base = GetLoadedMachine(self.dim, self.x, self.y - 1, self.z)
        if not isinstance(base, SpecializedGrowthBase):
            return
        self._exchange_running = True
        self._applying_recipe = True
        fluid_events = []
        changed = False
        try:
            changed = move_item(self, 3, base, base.item_output_slots) or changed
            changed = move_fluid(self, 1, base, 1, fluid_events) or changed
            changed = move_item(base, 0, self, (0,), validate_input=True) or changed
            changed = move_fluid(base, 0, self, 0, fluid_events, validate_input=True) or changed
            # 流体事件同步触发；双方库存一致后再通知，禁止中途选方或递归搬运。
            for machine, added, slot, fluid_id, amount in fluid_events:
                if added:
                    machine._on_added_fluid(slot, fluid_id, amount, True)
                else:
                    machine._on_reduced_fluid(slot, fluid_id, amount, True)
        finally:
            self._applying_recipe = False
            self._exchange_running = False
        if changed:
            self.recheck_recipe()
            self._output_dirty = True
            if self.current_recipe is not None:
                self._check_output()
            self.CallSync()
            base.CallSync()

    @accepts_slot_reads
    def finish_recipe(self, recipe, slot_reads=None):
        if not Processor.finish_recipe(self, recipe, slot_reads):
            return False
        self.ExchangeWithBase()
        return True
