# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockCardinalFacing,
    GetBlockNameAndAux,
    GetBlockStatesFromAuxValue,
    SetBlock,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events import (
    BlockNeighborChangedServerEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM
from ...common.define.id_enum import RESIN_COLLECTOR, RESIN
from ...common.define.id_enum.machinery import Machinery
from .basic import (
    BaseMachine,
    ItemContainer,
    RegisterMachine,
)
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(cable=True)


@RegisterMachine
class ResinCollectorOutputer(BaseMachine, ItemContainer):
    block_name = Machinery.RESIN_COLLECTOR_OUTPUTER
    is_non_energy_machine = True
    output_slots = (0,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.flush_resin_collector_pos()
        self.last_resin_storage = None

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        for facing, (dx, dz) in enumerate(FACING_DXZ):
            target_pos = (event.x + dx, event.y, event.z + dz)
            block_id, _ = GetBlockNameAndAux(
                event.dimensionId,
                target_pos,
            )
            if block_id == RESIN_COLLECTOR:
                its_facing = (
                    FACING_EN2NUM[GetBlockCardinalFacing(event.dimensionId, target_pos)]
                    - 2
                )
                if its_facing == facing:
                    return
        event.cancel()

    def OnPlaced(self, _):
        TCON.block_placed(self)
        for facing, (dx, dz) in enumerate(FACING_DXZ):
            block_id, _ = GetBlockNameAndAux(
                self.dim,
                (self.x + dx, self.y, self.z + dz),
            )
            if block_id != RESIN_COLLECTOR:
                continue
            self._set_facing(facing)
            break

    def OnBlockRandomTick(self, event):
        block_id, aux = GetBlockNameAndAux(self.dim, self.linked_resin_collector_pos)
        if block_id is None:
            return
        elif block_id != RESIN_COLLECTOR:
            self._destroy_self_later()
            return
        resin_storage = GetBlockStatesFromAuxValue(block_id, aux).get(
            "skybluetech:resin_storage", 0
        )
        if resin_storage == 0:
            return
        ok = self._try_add_resin()
        if ok:
            UpdateBlockStates(
                self.dim,
                self.linked_resin_collector_pos,
                {"skybluetech:resin_storage": resin_storage - 1},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)
        if (
            event.neighborPosX,
            event.neighborPosY,
            event.neighborPosZ,
        ) != self.linked_resin_collector_pos:
            return
        if event.toBlockName != RESIN_COLLECTOR:
            self._destroy_self_later()
            return
        resin_storage = GetBlockStatesFromAuxValue(
            RESIN_COLLECTOR, event.toAuxValue
        ).get("skybluetech:resin_storage", 0)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:resin_storage": resin_storage},
        )

    def flush_resin_collector_pos(self):
        facing = GetBlockCardinalFacing(self.dim, (self.x, self.y, self.z))
        if facing == "north":
            self.linked_resin_collector_pos = (self.x, self.y, self.z - 1)
        elif facing == "south":
            self.linked_resin_collector_pos = (self.x, self.y, self.z + 1)
        elif facing == "west":
            self.linked_resin_collector_pos = (self.x - 1, self.y, self.z)
        elif facing == "east":
            self.linked_resin_collector_pos = (self.x + 1, self.y, self.z)
        else:
            self.linked_resin_collector_pos = (self.x, self.y, self.z)

    def _destroy_self_later(self):
        SetBlock(
            self.dim, (self.x, self.y, self.z), "minecraft:air", old_block_handing=1
        )

    def _set_facing(self, facing):
        # type: (int) -> None
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"minecraft:cardinal_direction": FACING_EN[facing + 2]},
        )
        self.flush_resin_collector_pos()
        UpdateBlockStates(
            self.dim,
            self.linked_resin_collector_pos,
            {"skybluetech:is_connect_outputer": True},
        )

    def _try_add_resin(self):
        res = self.OutputItem(Item(RESIN))
        return res is None
