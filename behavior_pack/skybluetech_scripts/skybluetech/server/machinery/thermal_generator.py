# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item

from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.machinery_def.thermal_generator import (
    FUEL_SECONDS_MAP,
    K_BURN_SEC_LEFT,
    K_MAX_BURN_SEC,
    STORE_RF_MAX,
    TICK_POWER,
)
from .basic import (
    BaseGenerator,
    GUIControl,
    ItemContainer,
    WorkRenderer,
)
from .core import RegisterMachine

SECOND_PER_TICK = 0.05

BURN_SYNC_TICKS = 20  # 燃烧余量 bdata 同步间隔(1秒); 燃料耗尽/重新加料时立即同步


@RegisterMachine
class ThermalGenerator(WorkRenderer, GUIControl, ItemContainer, BaseGenerator):
    block_name = Machinery.THERMAL_GENERATOR
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    item_input_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ThermalGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self._burn_sync_tick = 0
        self._burn_seconds_left_mem = self.bdata[K_BURN_SEC_LEFT] or 0
        self.is_burning = self.burn_seconds_left > 0
        if self.IsActive() and self.burn_seconds_left > 0:
            self.SetOutputPower(TICK_POWER)
        else:
            self.SetOutputPower(0)
        self.handler.SubscribeOnTicking(self._thermal_generator_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._thermal_generator_on_slot_update)


    def _thermal_generator_on_ticking(self):
        if self.IsActive():
            if self.burn_seconds_left <= 0:
                self.is_burning = self.next_burn()
                return
            self.burn_seconds_left -= SECOND_PER_TICK

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            self._thermal_generator_is_valid_input(slot, item),
        )
        return all(results)

    def _thermal_generator_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        return item.newItemName != "minecraft:lava_bucket" and (
            item.id in FUEL_SECONDS_MAP or item.GetBasicInfo().fuelDuration > 0
        )

    def _thermal_generator_on_slot_update(self, slot_pos):
        # type: (int) -> None
        self.next_burn()


    def next_burn(self):
        if self.is_burning:
            return
        mainSlotItem = self.GetSlotItem(0)
        if mainSlotItem is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            self.is_burning = False
            return False
        burnTime = (
            FUEL_SECONDS_MAP.get(mainSlotItem.id)
            or mainSlotItem.GetBasicInfo().fuelDuration
        )
        if burnTime <= 0:
            return
        self.burn_seconds_left = burnTime
        self.max_burn_seconds = burnTime
        mainSlotItem.count -= 1
        self.SetSlotItem(0, mainSlotItem)
        self.is_burning = True
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        self.SetOutputPower(TICK_POWER)
        return True

    @property
    def burn_seconds_left(self):
        # type: () -> float
        return self._burn_seconds_left_mem

    @burn_seconds_left.setter
    def burn_seconds_left(self, value):
        # type: (float) -> None
        "写入节流: 燃烧余量以内存镜像为准, bdata 每 BURN_SYNC_TICKS tick 同步一次; 燃料耗尽/重新加料立即同步。"
        self._burn_sync_tick += 1
        if (
            value <= 0
            or value > self._burn_seconds_left_mem
            or self._burn_sync_tick % BURN_SYNC_TICKS == 0
        ):
            self.bdata[K_BURN_SEC_LEFT] = value
        self._burn_seconds_left_mem = value

    @property
    def max_burn_seconds(self):
        # type: () -> float
        return self.bdata[K_MAX_BURN_SEC] or 1

    @max_burn_seconds.setter
    def max_burn_seconds(self, value):
        # type: (float) -> None
        self.bdata[K_MAX_BURN_SEC] = value
