# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import UpdateBlockStates, GetBlockName
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.id_enum import GAS_BURNING_GENERATOR as MACHINE_ID
from ...common.define.facing import DXYZ_FACING, FACING_EN
from ...common.machinery_def.gas_burning_generator import recipes as Recipes
from ...common.ui_sync.machinery.gas_burning_generator import (
    GasBurningGeneratorUISync,
    FluidSlotSync,
)
from ..transmitters.pipe.logic import isPipe
from .basic import (
    BaseGenerator,
    GUIControl,
    MultiFluidContainer,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)


@RegisterMachine
class GasBurningGenerator(
    BaseGenerator, GUIControl, MultiFluidContainer, UpgradeControl, WorkRenderer
):
    block_name = MACHINE_ID
    store_rf_max = 28800
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (2000, 2000)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = GasBurningGeneratorUISync.NewServer(self).Activate()
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isPipe(bname)
            UpdateBlockStates(
                self.dim,
                (self.x, self.y, self.z),
                {"skybluetech:%s_pipe_connection" % facing_en: connectToWire},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        connectToWire = isPipe(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:%s_pipe_connection" % facing_en: connectToWire},
        )

    def OnTicking(self):
        if self.IsActive():
            if self.burn_once():
                self.CallSync()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in Recipes

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = float(self.fluids[0].volume) / self.fluids[0].max_volume
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

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

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    @SuperExecutorMeta.execute_super
    def UnsetDeactiveFlag(self, flag, flush=True):
        pass

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
        self.GeneratePower(rcp.output_power)
        return True
