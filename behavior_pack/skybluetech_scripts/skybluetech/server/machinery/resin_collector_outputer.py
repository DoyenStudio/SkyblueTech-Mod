# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.events import (
    BlockNeighborChangedServerEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ...common.define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM
from ...common.define.id_enum import RESIN_COLLECTOR, Machinery
from ...common.define.id_enum.fluids import CommonLiquid
from ...common.define.resin import RESIN_FLUID_VOLUME, RESIN_OUTPUT_MAX_VOLUME
from ..transmitters.fluid_pipe.logic import is_fluid_pipe
from .basic import MultiFluidContainer
from .core import RegisterMachine
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(fluid_pipe=True)


@RegisterMachine
class ResinCollectorOutputer(MultiFluidContainer):
    block_name = Machinery.RESIN_COLLECTOR_OUTPUTER
    is_non_energy_machine = True
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = (0,)
    fluid_slot_max_volumes = {0: RESIN_OUTPUT_MAX_VOLUME}
    allow_player_use_bucket_push = False

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ResinCollectorOutputer, self).__init__(dim, x, y, z, block_entity_data)
        self.flush_resin_collector_pos()
        self.handler.SubscribeOnPlaced(self._resin_collector_outputer_on_placed)
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
        # 等管道放置监听完成连通和建网后，再设置抽取模式。
        ExecLater(0, self._set_lower_pipe_output)
        for facing, (dx, dz) in enumerate(FACING_DXZ):
            block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                (self.x + dx, self.y, self.z + dz),
                self.dim,
            )
            block_id, _ = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
            if block_id != RESIN_COLLECTOR:
                continue
            collector_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
                (self.x + dx, self.y, self.z + dz), self.dim,
            )
            if not collector_states or collector_states.get("minecraft:cardinal_direction") != FACING_EN[facing + 2]:
                continue
            self._set_facing(facing)
            self.SyncResinStorage()
            break

    def _resin_collector_outputer_on_neighbor_changed(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)
        if (
            (event.neighborPosX, event.neighborPosY, event.neighborPosZ) == (self.x, self.y - 1, self.z)
            and event.fromBlockName != event.toBlockName
            and is_fluid_pipe(event.toBlockName)
        ):
            ExecLater(0, self._set_lower_pipe_output)
        self.flush_resin_collector_pos()
        if (
            event.neighborPosX,
            event.neighborPosY,
            event.neighborPosZ,
        ) != self.linked_resin_collector_pos:
            return
        if event.toBlockName != RESIN_COLLECTOR:
            self._destroy_self_later()
            return
        self.SyncResinStorage()

    def _set_lower_pipe_output(self):
        from ..transmitters.fluid_pipe.action import action_module

        block_info = CF.CreateBlockInfo(LEVEL_ID)
        if (block_info.GetBlockNew(self.xyz, self.dim) or {}).get("name") != self.block_name:
            return
        pipe_pos = (self.x, self.y - 1, self.z)
        pipe_name = (block_info.GetBlockNew(pipe_pos, self.dim) or {}).get("name")
        if not pipe_name or not is_fluid_pipe(pipe_name):
            return
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(pipe_pos, self.dim) or {}
        if not states.get("skybluetech:connection_up", False) or states.get("skybluetech:cable_io_up", False):
            return
        action_module.switch_access_mode(self.dim, self.x, self.y - 1, self.z, 1)
        TCON.block_placed(self)

    def SyncResinStorage(self):
        # type: () -> None
        # 采集斗保存唯一的硬化存量，输出斗仅镜像其模型状态。
        block_state_comp = CF.CreateBlockState(LEVEL_ID)
        collector_states = block_state_comp.GetBlockStates(self.linked_resin_collector_pos, self.dim)
        if collector_states is None:
            return
        resin_storage = collector_states.get("skybluetech:resin_storage", 0)
        block_states = block_state_comp.GetBlockStates((self.x, self.y, self.z), self.dim)
        if block_states is not None and block_states.get("skybluetech:resin_storage") != resin_storage:
            block_states.update({"skybluetech:resin_storage": resin_storage})
            block_state_comp.SetBlockStates((self.x, self.y, self.z), block_states, self.dim)

    def flush_resin_collector_pos(self):
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            (self.x, self.y, self.z),
            self.dim,
        ) or {}
        facing = states.get("minecraft:cardinal_direction")
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

    def TryCollectResin(self):
        # type: () -> bool
        collector_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            self.linked_resin_collector_pos, self.dim,
        )
        if collector_states is None or collector_states.get("skybluetech:resin_storage", 0) > 0:
            return False
        fluid = self.fluids[0]
        if not fluid.canMerge(CommonLiquid.LIQUID_RESIN):
            return False
        # 必须容纳整份；OutputFluid 本身允许部分接收，不能据此消耗整份树脂。
        if fluid.max_volume - fluid.volume < RESIN_FLUID_VOLUME:
            return False
        ok, remaining = self.OutputFluid(CommonLiquid.LIQUID_RESIN, RESIN_FLUID_VOLUME, 0, True)
        return ok and remaining == 0
