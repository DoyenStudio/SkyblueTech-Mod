# coding=utf-8
# lang: py2
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server.block import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.events.server.item import PlayerTryPutCustomContainerItemServerEvent
from skybluetech_scripts.tooldelta.api.server.block import GetBlockNameAndAux
from skybluetech_scripts.tooldelta.api.server.item import ItemExists
from ..machinery_def.pump import *
from ..define import flags as rf_flags
from ..ui_sync.machines.pump import PumpUISync
from .basic import (
    AutoSaver,
    BaseMachine,
    FluidContainer,
    GUIControl,
    ItemContainer,
    SPControl,
    RegisterMachine,
)


K_PUMP_TYPE = "pump_type"


@RegisterMachine
class Pump(AutoSaver, FluidContainer, GUIControl, ItemContainer, SPControl):
    block_name = "skybluetech:pump"
    store_rf_max = 8800
    running_power = 0
    input_slots = (0,)
    output_slots = (1,)
    fluid_io_mode = (2, 1, 2, 2, 2, 2)
    max_fluid_volume = 4000
    origin_process_ticks = 5

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = PumpUISync.NewServer(self).Activate()
        self.OnSync()
        self.onBlockChanged()
        self.last_1000mb = self.fluid_volume >= 1000

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        SPControl.OnLoad(self)
        self.pump_type = self.bdata[K_PUMP_TYPE] or M_AIR

    def OnPlaced(self, _):
        under_block_name, aux = GetBlockNameAndAux(self.dim, (self.x, self.y - 1, self.z))
        if under_block_name is None:
            self.pump_type = M_AIR
            return
        self.pump_type = M_TYPE_MAPPING.get((under_block_name, aux), M_AIR)
        self.onBlockChanged()

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    def Dump(self):
        BaseMachine.Dump(self)
        SPControl.Dump(self)
        FluidContainer.Dump(self)
        self.bdata[K_PUMP_TYPE] = self.pump_type

    def OnTicking(self):
        while self.IsActive():
            if self.pump_type == M_AIR:
                self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_NO_RECIPE)
                return
            if self.fluid_id is None:
                self.fluid_id, _ = M_TYPE_MAPPING_REVERSE[self.pump_type]
            do_break = False
            if self.ProcessOnce():
                self.fluid_volume = min(self.max_fluid_volume, self.fluid_volume + self.pump_speed)
                self.OnSync()
                if not self.last_1000mb and self.fluid_volume >= 1000:
                    self.last_1000mb = True
                    self.OnSlotUpdate(None)
            else:
                do_break = True
            if self.fluid_volume >= self.max_fluid_volume:
                self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_FULL)
            if do_break:
                break

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    def OnCustomCotainerPutItem(self, event):
        # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
        if not self.IsValidInput(event.collectionIndex, event.item):
            event.cancel()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot not in self.input_slots:
            return False
        elif item.newItemName != "minecraft:bucket":
            # TODO: 兼容其他桶类似物
            return False
        return True

    def OnSlotUpdate(self, _):
        input_slot_item = self.GetSlotItem(0)
        output_slot_item = self.GetSlotItem(1)
        if input_slot_item is None:
            return
        if (
            output_slot_item is not None
            and output_slot_item.count >= output_slot_item.GetBasicInfo().maxStackSize
        ):
            return
        # NOTE: 我们假设水桶命名为 液体id_bucket
        if self.fluid_id is None:
            return
        excepted_output = self.fluid_id + "_bucket"
        if not ItemExists(excepted_output):
            return
        if output_slot_item is None:
            output_slot_item = Item(excepted_output, 0)
        can_output, _, _ = self.RequireFluid(None, 1000, True)
        if can_output:
            output_slot_item.count += 1
            self.SetSlotItem(1, output_slot_item)
            input_slot_item.count -= 1
            self.SetSlotItem(0, input_slot_item)
            self.OnSync()
            if (
                self.HasDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_FULL)
                and self.fluid_volume < self.max_fluid_volume
            ):
                self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_FULL)
            if self.fluid_volume < 1000:
                self.last_1000mb = False

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if event.neighborPosX != self.x or event.neighborPosY != self.y - 1 or event.neighborPosZ != self.z:
            return
        under_block_name = event.toBlockName
        self.pump_type = M_TYPE_MAPPING.get((under_block_name, event.toAuxValue), M_AIR)
        self.onBlockChanged()

    def onBlockChanged(self):
        self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_NO_RECIPE)
        if self.pump_type != M_AIR and self.fluid_id is not None and M_TYPE_MAPPING_REVERSE[self.pump_type][0] != self.fluid_id:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_NOT_MATCH)
        # elif self.HasDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_NOT_MATCH):
        #     self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_FLUID_NOT_MATCH)
        if self.pump_type != M_AIR:
            self.SetPower(PUMP_FLUID_AND_POWER[self.pump_type])
            self.pump_speed = PUMP_SPEED[self.pump_type]
            self.fluid_id, _ = M_TYPE_MAPPING_REVERSE[self.pump_type]
        else:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_NO_RECIPE)
            self.SetPower(0)
            self.pump_speed = 0
            self.pump_type = M_AIR
