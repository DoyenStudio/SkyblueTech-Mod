# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    UpdateBlockStates,
    GetBlockName,
    ItemExists,
)
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define.global_config import BUCKET_VOLUME
from ....common.define.facing import DXYZ_FACING, FACING_EN
from ....common.ui_sync.machinery.general_tank import GeneralTankUISync
from ...transmitters.pipe.logic import isPipe
from ..basic import BaseMachine, FluidContainer, ItemContainer, GUIControl

INFINITY = float("inf")
registered_tanks = {}  # type: dict[str, type[BasicTank]]
FIRST_TANK_LOADED = False


class BasicTank(BaseMachine, FluidContainer, ItemContainer, GUIControl):
    is_non_energy_machine = True
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = 0
    max_fluid_volume = 0
    input_slots = (0,)
    output_slots = (1,)

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = GeneralTankUISync.NewServer(self).Activate()

    def OnSync(self):
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnTryActivate(self):
        pass

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
                {"skybluetech:connection_" + facing_en: connectToWire},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        connectToWire = isPipe(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire},
        )

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        item0 = self.GetSlotItem(0)
        item1 = self.GetSlotItem(1)
        if item0 is not None:
            if item0.id == "minecraft:bucket":
                if (
                    item1 is not None
                    or self.fluid_id is None
                    or self.fluid_volume < BUCKET_VOLUME
                ):
                    return
                fluid_id = self.fluid_id
                bucket_id = fluid_id + "_bucket"
                if not ItemExists(bucket_id):
                    return
                # TODO: 我们只能假定桶 id 是液体 id + "_bucket"
                self.fluid_volume -= BUCKET_VOLUME
                if self.fluid_volume <= 0:
                    self.fluid_id = None
                self.SetSlotItem(1, Item(bucket_id))
                item0.count -= 1
                self.SetSlotItem(0, item0)
                self.onReducedFluid(fluid_id, BUCKET_VOLUME)
                self.CallSync()
            elif item0.id.endswith("_bucket"):
                if item1 is not None and (
                    item1.id != "minecraft:bucket" or item1.StackFull()
                ):
                    return
                fluid_id = item0.id[: -len("_bucket")]
                if (
                    (self.fluid_id is not None and self.fluid_id != fluid_id)
                    or self.fluid_volume + BUCKET_VOLUME > self.max_fluid_volume
                    or not ItemExists(fluid_id)
                ):
                    return
                if self.fluid_id is None:
                    self.fluid_id = fluid_id
                self.fluid_volume += BUCKET_VOLUME
                self.SetSlotItem(0, None)
                if item1 is None:
                    item1 = Item("minecraft:bucket", count=0)
                    # TODO: 如果其他模组的捅倒空不是 minecraft:bucket 则出问题
                item1.count += 1
                self.SetSlotItem(1, item1)
                self.onAddedFluid(fluid_id, BUCKET_VOLUME)
                self.CallSync()


def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class
