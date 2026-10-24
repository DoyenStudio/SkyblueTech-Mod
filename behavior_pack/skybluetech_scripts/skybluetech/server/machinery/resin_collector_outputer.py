# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events import (
    BlockNeighborChangedServerEvent,
    ServerEntityTryPlaceBlockEvent,
)

from ...common.define import flags
from ...common.define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM
from ...common.define.id_enum import RESIN, RESIN_COLLECTOR, Machinery
from .basic import (
    BaseMachine,
    ItemContainer,
)
from .core import RegisterMachine
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(item_pipe=True)


@RegisterMachine
class ResinCollectorOutputer(ItemContainer):
    block_name = Machinery.RESIN_COLLECTOR_OUTPUTER
    is_non_energy_machine = True
    item_output_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ResinCollectorOutputer, self).__init__(dim, x, y, z, block_entity_data)
        self.flush_resin_collector_pos()
        self.last_resin_storage = None
        self.handler.SubscribeOnPlaced(self._resin_collector_outputer_on_placed)
        self.handler.SubscribeOnBlockRandomTick(self._resin_collector_outputer_on_block_random_tick)
        self.handler.SubscribeOnNeighborChanged(self._resin_collector_outputer_on_neighbor_changed)

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        for facing, (dx, dz) in enumerate(FACING_DXZ):
            target_pos = (event.x + dx, event.y, event.z + dz)
            block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(target_pos, event.dimensionId)
            block_id, _ = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
            if block_id == RESIN_COLLECTOR:
                its_facing = (
                    FACING_EN2NUM[CF.CreateBlockState(LEVEL_ID).GetBlockStates(
                        target_pos,
                        event.dimensionId,
                    )["minecraft:cardinal_direction"]]
                    - 2
                )
                if its_facing == facing:
                    return
        event.cancel()

    def _resin_collector_outputer_on_placed(self, _):
        TCON.block_placed(self)
        for facing, (dx, dz) in enumerate(FACING_DXZ):
            block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                (self.x + dx, self.y, self.z + dz),
                self.dim,
            )
            block_id, _ = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
            if block_id != RESIN_COLLECTOR:
                continue
            self._set_facing(facing)
            break

    def _resin_collector_outputer_on_block_random_tick(self, event):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
            self.linked_resin_collector_pos,
            self.dim,
        )
        block_id, aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
        if block_id is None:
            return
        elif block_id != RESIN_COLLECTOR:
            self._destroy_self_later()
            return
        resin_storage = CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(block_id, aux).get(
            "skybluetech:resin_storage", 0
        )
        if resin_storage == 0:
            return
        ok = self._try_add_resin()
        if ok:
            block_state_comp = CF.CreateBlockState(LEVEL_ID)
            block_states = block_state_comp.GetBlockStates(self.linked_resin_collector_pos, self.dim)
            if block_states is not None:
                block_states.update({"skybluetech:resin_storage": resin_storage - 1})
                block_state_comp.SetBlockStates(self.linked_resin_collector_pos, block_states, self.dim)

    def _resin_collector_outputer_on_neighbor_changed(self, event):
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
        resin_storage = CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(RESIN_COLLECTOR, event.toAuxValue).get(
            "skybluetech:resin_storage",
            0,
        )
        block_state_comp = CF.CreateBlockState(LEVEL_ID)
        block_states = block_state_comp.GetBlockStates((self.x, self.y, self.z), self.dim)
        if block_states is not None:
            block_states.update({"skybluetech:resin_storage": resin_storage})
            block_state_comp.SetBlockStates((self.x, self.y, self.z), block_states, self.dim)

    def flush_resin_collector_pos(self):
        facing = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            (self.x, self.y, self.z),
            self.dim,
        )["minecraft:cardinal_direction"]
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
        CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
            (self.x, self.y, self.z),
            {"name": "minecraft:air", "aux": 0},
            1,
            dimensionId=self.dim,
        )

    def _set_facing(self, facing):
        # type: (int) -> None
        block_state_comp = CF.CreateBlockState(LEVEL_ID)
        block_states = block_state_comp.GetBlockStates((self.x, self.y, self.z), self.dim)
        if block_states is not None:
            block_states.update({"minecraft:cardinal_direction": FACING_EN[facing + 2]})
            block_state_comp.SetBlockStates((self.x, self.y, self.z), block_states, self.dim)
        self.flush_resin_collector_pos()
        block_state_comp = CF.CreateBlockState(LEVEL_ID)
        block_states = block_state_comp.GetBlockStates(self.linked_resin_collector_pos, self.dim)
        if block_states is not None:
            block_states.update({"skybluetech:is_connect_outputer": True})
            block_state_comp.SetBlockStates(self.linked_resin_collector_pos, block_states, self.dim)

    def _try_add_resin(self):
        res = self.OutputItem(Item(RESIN))
        return res is None
