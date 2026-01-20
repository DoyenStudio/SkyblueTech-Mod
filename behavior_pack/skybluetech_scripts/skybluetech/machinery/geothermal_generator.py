# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..define import flags
from ..define.id_enum.machinery import GEO_THERMAL_GENERATOR as MACHINE_ID
from ..machinery_def.geothermal_generator import *
from ..ui_sync.machinery.geothermal_generator import GeoThermalGeneratorUISync, FluidSlotSync
from .basic import AutoSaver, BasicGenerator, MultiFluidContainer, GUIControl, WorkRenderer, RegisterMachine

K_BURN_TICKS_LEFT = "burn_ticks_left"
K_POWER = "power"


@RegisterMachine
class GeoThermalGenerator(AutoSaver, BasicGenerator, GUIControl, MultiFluidContainer, WorkRenderer):
    block_name = MACHINE_ID
    store_rf_max = 28800
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = {0, 1}
    fluid_io_fix_mode = 0

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BasicGenerator.__init__(self, dim, x, y, z, block_entity_data)
        MultiFluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = GeoThermalGeneratorUISync.NewServer(self).Activate()

    def OnTicking(self):
        if self.IsActive():
            self.burn_ticks -= 1
            if self.burn_ticks <= 0:
                if self.store_rf == self.store_rf_max:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
                    return
                self.next_burn()
                if self.power == 0:
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
                    return
            self.GeneratePower(self.power)
            self.OnSync()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return (
            (slot == 0 and fluid_id == "minecraft:lava")
            or
            (slot == 1 and fluid_id == "minecraft:water")
        )

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = float(self.burn_ticks) / ONCE_BURNING_TICKS
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()

    def OnLoad(self):
        BasicGenerator.OnLoad(self)
        data = self.bdata
        self.burn_ticks = data[K_BURN_TICKS_LEFT] or 0
        self.power = data[K_POWER] or 0

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        BasicGenerator.OnUnload(self)
        GUIControl.OnUnload(self)

    def Dump(self):
        BasicGenerator.Dump(self)
        MultiFluidContainer.Dump(self)
        self.bdata[K_BURN_TICKS_LEFT] = self.burn_ticks
        self.bdata[K_POWER] = 0
        self.OnSync()

    def OnTryActivate(self):
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL) and self.store_rf < self.store_rf_max:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def OnFluidSlotUpdate(self, slot):
        if slot != 0:
            return
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
            ok = self.next_burn()
            if ok:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    def next_burn(self):
        self.power = 0
        f0, f1 = self.fluids
        self.RequireAnyFluidFromNetwork()
        if f0.fluid_id == LAVA_ID and f0.volume > ONCE_LAVA_REDUCE_VOLUME:
            f0.volume -= ONCE_LAVA_REDUCE_VOLUME
            if f1.fluid_id == WATER_ID and f1.volume > ONCE_WATER_REDUCE_VOLUME:
                f1.volume -= ONCE_WATER_REDUCE_VOLUME
                self.power = GENERATED_POWER_WITH_WATER
            else:
                self.power = ORIGIN_GENERATED_POWER
            self.burn_ticks = ONCE_BURNING_TICKS
            return True
        self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        return False

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BasicGenerator.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)
