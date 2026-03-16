# coding=utf-8
import random
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from ...common.define import flags
from ...common.define.id_enum import GAS_BURNING_GENERATOR as MACHINE_ID
from ...common.machinery_def.gas_burning_generator import recipes as Recipes
from ...common.ui_sync.machinery.gas_burning_generator import (
    GasBurningGeneratorUISync,
    FluidSlotSync,
)
from .basic import (
    BasicGenerator,
    GUIControl,
    MultiFluidContainer,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)


@RegisterMachine
class GasBurningGenerator(
    BasicGenerator, GUIControl, MultiFluidContainer, UpgradeControl, WorkRenderer
):
    block_name = MACHINE_ID
    store_rf_max = 28800
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = {0}
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (2000, 2000)
    output_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BasicGenerator.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        MultiFluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = GasBurningGeneratorUISync.NewServer(self).Activate()
        self.CallSync()
        self.power = 0

    def OnTicking(self):
        if self.IsActive():
            if self.burn_once():
                self.GeneratePower(self.power)
                self.OnSync()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in Recipes

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = self.fluids[0].volume / self.fluids[0].max_volume
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()

    def OnUnload(self):
        BasicGenerator.OnUnload(self)
        GUIControl.OnUnload(self)

    def OnTryActivate(self):
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
        MultiFluidContainer.OnTryActivate(self)

    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if slot != 0:
            return
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, flush=False)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE, flush=False)

    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        if slot != 1:
            return
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, flush=False)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BasicGenerator.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def UnsetDeactiveFlag(self, flag, flush=True):
        WorkRenderer.UnsetDeactiveFlag(self, flag, flush)

    def get_recipe(self):
        input_gas = self.fluids[0]
        output_gas = self.fluids[1]
        input_gas_id = input_gas.fluid_id
        if input_gas_id is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return None
        rcp = Recipes.get(input_gas_id)
        if rcp is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return None
        elif input_gas.volume < rcp.once_burning_volume:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return None
        elif rcp.output_gas_id is not None and (
            output_gas.fluid_id != rcp.output_gas_id
            or rcp.output_gas_volume > output_gas.max_volume - output_gas.volume
        ):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return None
        return rcp

    def burn_once(self):
        input_gas = self.fluids[0]
        output_gas = self.fluids[1]
        rcp = self.get_recipe()
        if rcp is None:
            return False
        input_gas.volume -= rcp.once_burning_volume
        if input_gas.volume <= 0:
            input_gas.fluid_id = None
        if rcp.output_gas_id is not None:
            output_gas.fluid_id = rcp.output_gas_id
            output_gas.volume += rcp.output_gas_volume
        return True
