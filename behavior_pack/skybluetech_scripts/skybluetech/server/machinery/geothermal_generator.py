# coding=utf-8
import random
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.tooldelta.define import Item
from ...common.define import flags
from ...common.define.id_enum import GEO_THERMAL_GENERATOR as MACHINE_ID, Dusts
from ...common.machinery_def.geothermal_generator import (
    WATER_ID,
    LAVA_ID,
    ONCE_BURNING_TICKS,
    ONCE_LAVA_REDUCE_VOLUME,
    ONCE_WATER_REDUCE_VOLUME,
    ORIGIN_GENERATED_POWER,
    GENERATED_POWER_WITH_WATER,
)
from ...common.ui_sync.machinery.geothermal_generator import (
    GeoThermalGeneratorUISync,
    FluidSlotSync,
)
from .basic import (
    BaseGenerator,
    GUIControl,
    ItemContainer,
    MultiFluidContainer,
    WorkRenderer,
    RegisterMachine,
)

K_BURN_TICKS_LEFT = "burn_ticks_left"


@RegisterMachine
class GeoThermalGenerator(
    BaseGenerator, GUIControl, ItemContainer, MultiFluidContainer, WorkRenderer
):
    block_name = MACHINE_ID
    store_rf_max = 28800
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = {0, 1}
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (2000, 2000)
    output_slots = (0,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = GeoThermalGeneratorUISync.NewServer(self).Activate()
        self.CallSync()
        self.power = 0

    def OnTicking(self):
        if self.IsActive():
            self.burn_ticks -= 1
            if self.burn_ticks <= 0:
                if self.store_rf == self.store_rf_max:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
                    return
                res = self.next_burn()
                if not res:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            self.GeneratePower(self.power)
            self.CallSync()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id == {
            0: LAVA_ID,
            1: WATER_ID,
        }.get(slot)

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = float(self.burn_ticks) / ONCE_BURNING_TICKS
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def OnTryActivate(self):
        self.GeneratePower(0)
        if (
            self.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
            and self.store_rf < self.store_rf_max
        ):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if slot != 0:
            return
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
            ok = self.next_burn()
            if ok:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos == 0 and self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
            slotitem = self.GetSlotItem(0)
            if slotitem is None or (
                slotitem.id == Dusts.OBSIDIAN and not slotitem.StackFull()
            ):
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    def next_burn(self):
        self.power = 0
        f0, f1 = self.fluids
        if f0.fluid_id == LAVA_ID and f0.volume >= ONCE_LAVA_REDUCE_VOLUME:
            f0.volume -= ONCE_LAVA_REDUCE_VOLUME
            if f1.fluid_id == WATER_ID and f1.volume >= ONCE_WATER_REDUCE_VOLUME:
                f1.volume -= ONCE_WATER_REDUCE_VOLUME
                self.power = GENERATED_POWER_WITH_WATER
            else:
                self.power = ORIGIN_GENERATED_POWER
            self.burn_ticks = ONCE_BURNING_TICKS
            if random.random() > 0.9:
                rest = self.OutputItem(Item(Dusts.OBSIDIAN))
                if rest is not None:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return True
        return False

    @property
    def burn_ticks(self):
        # type: () -> int
        return self.bdata[K_BURN_TICKS_LEFT] or 0

    @burn_ticks.setter
    def burn_ticks(self, value):
        # type: (int) -> None
        self.bdata[K_BURN_TICKS_LEFT] = value
