# coding=utf-8
import random

from skybluetech_scripts.tooldelta.define import Item

from ...common.define import flags
from ...common.define.id_enum import Dusts, Machinery
from ...common.machinery_def.geothermal_generator import (
    GENERATED_POWER_WITH_WATER,
    K_BURN_TICKS_LEFT,
    K_OUTPUT_POWER,
    LAVA_ID,
    MAX_LAVA_VOLUME,
    MAX_WATER_VOLUME,
    ONCE_BURNING_TICKS,
    ONCE_LAVA_REDUCE_VOLUME,
    ONCE_WATER_REDUCE_VOLUME,
    ORIGIN_GENERATED_POWER,
    STORE_RF_MAX,
    WATER_ID,
)
from .basic import (
    BaseGenerator,
    GUIControl,
    ItemContainer,
    MultiFluidContainer,
    WorkRenderer,
)
from .core import RegisterMachine


@RegisterMachine
class GeoThermalGenerator(
    WorkRenderer,
    MultiFluidContainer,
    ItemContainer,
    GUIControl,
    BaseGenerator,
):
    block_name = Machinery.GEO_THERMAL_GENERATOR
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = {0, 1}
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (MAX_LAVA_VOLUME, MAX_WATER_VOLUME)
    output_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(GeoThermalGenerator, self).__init__(dim, x, y, z, block_entity_data)
        if self.burn_ticks > 0:
            self.SetOutputPower(self.bdata[K_OUTPUT_POWER] or ORIGIN_GENERATED_POWER)
        self.handler.SubscribeOnTicking(self._geo_thermal_generator_on_ticking)
        self.handler.SubscribeOnAddedFluid(self._geo_thermal_generator_on_added_fluid)
        self.handler.SubscribeOnSlotUpdate(self._geo_thermal_generator_on_slot_update)

    def _geo_thermal_generator_on_ticking(self):
        if self.IsActive():
            self.burn_ticks -= 1
            if self.burn_ticks <= 0:
                res = self.next_burn()
                if not res:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        results = (
            MultiFluidContainer.IsValidFluidInput(self, slot, fluid_id),
            self._geo_thermal_generator_is_valid_fluid_input(slot, fluid_id),
        )
        return all(results)

    def _geo_thermal_generator_is_valid_fluid_input(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id == {
            0: LAVA_ID,
            1: WATER_ID,
        }.get(slot)


    def _geo_thermal_generator_on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if slot != 0:
            return
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
            ok = self.next_burn()
            if ok:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    def _geo_thermal_generator_on_slot_update(self, slot_pos):
        # type: (int) -> None
        if slot_pos == 0 and self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
            slotitem = self.GetSlotItem(0)
            if slotitem is None or (
                slotitem.id == Dusts.OBSIDIAN and not slotitem.StackFull()
            ):
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)


    def next_burn(self):
        self.SetOutputPower(0)
        f0, f1 = self.fluids
        if f0.fluid_id == LAVA_ID and f0.volume >= ONCE_LAVA_REDUCE_VOLUME:
            f0.volume -= ONCE_LAVA_REDUCE_VOLUME
            if f1.fluid_id == WATER_ID and f1.volume >= ONCE_WATER_REDUCE_VOLUME:
                f1.volume -= ONCE_WATER_REDUCE_VOLUME
                self.SetOutputPower(GENERATED_POWER_WITH_WATER)
            else:
                self.SetOutputPower(ORIGIN_GENERATED_POWER)
            self.burn_ticks = ONCE_BURNING_TICKS
            if random.random() > 0.9:
                rest = self.OutputItem(Item(Dusts.OBSIDIAN))
                if rest is not None:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return True
        return False

    def SetOutputPower(self, power):
        # type: (int) -> None
        BaseGenerator.SetOutputPower(self, power)
        self.bdata[K_OUTPUT_POWER] = power

    @property
    def burn_ticks(self):
        # type: () -> int
        return self.bdata[K_BURN_TICKS_LEFT] or 0

    @burn_ticks.setter
    def burn_ticks(self, value):
        # type: (int) -> None
        self.bdata[K_BURN_TICKS_LEFT] = value
