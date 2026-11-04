# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
import random

from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    BlockRandomTickServerEvent,
    ServerEntityTryPlaceBlockEvent,
    ServerItemUseOnEvent,
)
from ...common.define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM
from ...common.define.id_enum import RESIN_COLLECTOR, Machinery
from ...common.define.id_enum.items import RESIN, RESIN_SPOON
from ...common.define.resin import MAX_RESIN_STORAGE
from ..machinery.core.pool import GetLoadedMachine
from ..machinery.resin_collector_outputer import ResinCollectorOutputer


@ServerEntityTryPlaceBlockEvent.Listen()
def onBlockPlace(event):
    # type: (ServerEntityTryPlaceBlockEvent) -> None
    if event.fullName != RESIN_COLLECTOR:
        return
    for i, (dx, dz) in enumerate(FACING_DXZ):
        nblock_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
            (event.x + dx, event.y, event.z + dz),
            event.dimensionId,
        ) or {}).get("name")
        if nblock_id != "minecraft:oak_log":
            continue
        ExecLater(0, set_collector_facing, event.dimensionId,
                  (event.x, event.y, event.z), FACING_EN[i + 2])
        return
    event.cancel()


def set_collector_facing(dim, pos, facing):
    # type: (int, tuple[int, int, int], str) -> None
    block_state = CF.CreateBlockState(LEVEL_ID)
    states = block_state.GetBlockStates(pos, dim)
    if states is None:
        return
    states["minecraft:cardinal_direction"] = facing
    block_state.SetBlockStates(pos, states, dim)


@BlockRandomTickServerEvent.Listen()
def onBlockRandomTick(event):
    # type: (BlockRandomTickServerEvent) -> None
    if event.fullName != RESIN_COLLECTOR:
        return
    if random.random() < 0.75:
        return
    blockstates = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
        (event.posX, event.posY, event.posZ),
        event.dimensionId,
    )
    if blockstates is None:
        return
    facing = FACING_EN2NUM[blockstates["minecraft:cardinal_direction"]]
    dx, dz = FACING_DXZ[facing - 2]
    res = log_is_in_tree(
        event.dimensionId, event.posX + dx, event.posY, event.posZ + dz
    )
    if res != 0:
        return
    resin_storage = blockstates["skybluetech:resin_storage"]
    if resin_storage >= MAX_RESIN_STORAGE:
        return
    outputer_pos = (event.posX - dx, event.posY, event.posZ - dz)
    if (
        blockstates.get("skybluetech:is_connect_outputer", False)
        and not CF.CreateChunkSource(LEVEL_ID).CheckChunkState(event.dimensionId, outputer_pos)
    ):
        return
    outputer_block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(outputer_pos, event.dimensionId) or {}
    if (
        outputer_block.get("name") == Machinery.RESIN_COLLECTOR_OUTPUTER
        and GetLoadedMachine(event.dimensionId, *outputer_pos) is None
    ):
        # 等待相邻区块中的液槽加载，不能把暂不可读误判为满槽硬化。
        return
    outputer = get_linked_outputer(
        event.dimensionId, (event.posX, event.posY, event.posZ), blockstates,
    )
    # 只把新生成的树脂送入液槽；已有 state 树脂全部视为硬化。
    if resin_storage == 0 and outputer is not None and outputer.TryCollectResin():
        return
    blockstates.update({"skybluetech:resin_storage": resin_storage + 1})
    CF.CreateBlockState(LEVEL_ID).SetBlockStates(
        (event.posX, event.posY, event.posZ),
        blockstates,
        event.dimensionId,
    )
    if outputer is not None:
        outputer.SyncResinStorage()


def get_linked_outputer(dim, collector_pos, collector_states):
    # type: (int, tuple[int, int, int], dict) -> ResinCollectorOutputer | None
    facing = FACING_EN2NUM[collector_states["minecraft:cardinal_direction"]]
    dx, dz = FACING_DXZ[facing - 2]
    x, y, z = collector_pos
    outputer = GetLoadedMachine(dim, x - dx, y, z - dz)
    if not isinstance(outputer, ResinCollectorOutputer):
        return None
    outputer.flush_resin_collector_pos()
    if outputer.linked_resin_collector_pos != collector_pos:
        return None
    if not collector_states.get("skybluetech:is_connect_outputer", False):
        collector_states["skybluetech:is_connect_outputer"] = True
        CF.CreateBlockState(LEVEL_ID).SetBlockStates(collector_pos, collector_states, dim)
    return outputer


@ServerItemUseOnEvent.ListenWithUserData()
def onItemUseOnEvent(event):
    # type: (ServerItemUseOnEvent) -> None
    if event.item.id != RESIN_SPOON or event.blockName not in (RESIN_COLLECTOR, Machinery.RESIN_COLLECTOR_OUTPUTER):
        return
    collector_pos = (event.x, event.y, event.z)
    if event.blockName == Machinery.RESIN_COLLECTOR_OUTPUTER:
        outputer = GetLoadedMachine(event.dimensionId, event.x, event.y, event.z)
        if not isinstance(outputer, ResinCollectorOutputer):
            return
        outputer.flush_resin_collector_pos()
        collector_pos = outputer.linked_resin_collector_pos
        if (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(collector_pos, event.dimensionId) or {}).get("name") != RESIN_COLLECTOR:
            return
    collector_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
        collector_pos,
        event.dimensionId,
    )
    if collector_states is None:
        return
    linked_outputer = get_linked_outputer(event.dimensionId, collector_pos, collector_states)
    if event.blockName == Machinery.RESIN_COLLECTOR_OUTPUTER and linked_outputer is not outputer:
        return
    resin_store = collector_states["skybluetech:resin_storage"]
    if resin_store <= 0:
        return
    durability = event.item.durability or event.item.GetBasicInfo().maxDurability
    durability -= 1
    event.item.durability = durability
    collector_states.update({"skybluetech:resin_storage": resin_store - 1})
    CF.CreateBlockState(LEVEL_ID).SetBlockStates(
        collector_pos,
        collector_states,
        event.dimensionId,
    )
    if linked_outputer is not None:
        linked_outputer.SyncResinStorage()
    if event.item.durability == 0:
        CF.CreateItem(event.entityId).SpawnItemToPlayerCarried(
            Item("minecraft:air").marshal(),
            event.entityId,
        )
    else:
        CF.CreateItem(event.entityId).SpawnItemToPlayerCarried(event.item.marshal(), event.entityId)
    GetServer().CreateEngineItemEntity(Item(RESIN).marshal(), event.dimensionId, (event.x + 0.5, event.y + 0.5, event.z + 0.5))


@BlockNeighborChangedServerEvent.Listen()
def onNeighborChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.blockName != RESIN_COLLECTOR:
        return
    if (
        event.fromBlockName == "minecraft:oak_log"
        and event.toBlockName != "minecraft:oak_log"
    ):
        blockstates = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            (event.posX, event.posY, event.posZ),
            event.dimensionId,
        )
        facing = FACING_EN2NUM[blockstates["minecraft:cardinal_direction"]]
        dx, dz = FACING_DXZ[facing - 2]
        if (
            event.posX + dx == event.neighborPosX
            and event.posZ + dz == event.neighborPosZ
            and event.posY == event.neighborPosY
        ):
            CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                (event.posX, event.posY, event.posZ),
                {"name": "minecraft:air", "aux": 0},
                1,
                dimensionId=event.dimensionId,
            )
        resin_drop = blockstates["skybluetech:resin_storage"] // 2
        GetServer().CreateEngineItemEntity(Item(RESIN, count=resin_drop).marshal(), event.dimensionId, (event.posX + 0.5, event.posY + 0.5, event.posZ + 0.5))
    elif event.fromBlockName == Machinery.RESIN_COLLECTOR_OUTPUTER:
        # 连接此树脂采集斗的树脂输出器被挖掉等
        if (
            event.toBlockName == Machinery.RESIN_COLLECTOR_OUTPUTER
            and event.toAuxValue == event.fromBlockAuxValue
        ):
            return
        prev_facing = FACING_EN2NUM[
            CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(
                Machinery.RESIN_COLLECTOR_OUTPUTER,
                event.fromBlockAuxValue,
            )["minecraft:cardinal_direction"]
        ]
        dx, dz = FACING_DXZ[prev_facing - 2]
        if (
            event.neighborPosX + dx != event.posX
            or event.neighborPosY != event.posY
            or event.neighborPosZ + dz != event.posZ
        ):
            return
        if event.toBlockName == Machinery.RESIN_COLLECTOR_OUTPUTER:
            current_facing = FACING_EN2NUM[
                CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(
                    Machinery.RESIN_COLLECTOR_OUTPUTER,
                    event.toAuxValue,
                )["minecraft:cardinal_direction"]
            ]
            dx2, dz2 = FACING_DXZ[current_facing - 2]
            # 原连接到此树脂采集斗的树脂输出器被诸如机械动力扳手这样的东西调整方向
            disconnect = (
                event.neighborPosX + dx2 != event.posX
                or event.neighborPosZ + dz2 != event.posZ
            )
        else:
            disconnect = True

        if disconnect:
            _block_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
                (event.posX, event.posY, event.posZ),
                event.dimensionId,
            )
            if _block_states is not None:
                _block_states.update({"skybluetech:is_connect_outputer": False})
                CF.CreateBlockState(LEVEL_ID).SetBlockStates(
                    (event.posX, event.posY, event.posZ),
                    _block_states,
                    event.dimensionId,
                )


def log_is_in_tree(dim, x, y, z):
    # type: (int, int, int, int) -> int
    upper_logs_count = 0
    leaves_count = 0
    if (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
        (x, y - 1, z),
        dim,
    ) or {}).get("name") != "minecraft:oak_log":
        return -1
    for _y in range(y, y + 20):
        block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew((x, _y, z), dim) or {}).get("name")
        if block_id == "minecraft:oak_log":
            upper_logs_count += 1
        elif block_id == "minecraft:oak_leaves":
            leaves_count += 1
        else:
            break
    for _y in range(y - 2, y - 6, -1):
        block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew((x, _y, z), dim) or {}).get("name")
        if block_id == "minecraft:dirt" or block_id == "minecraft:grass_block":
            break
        elif block_id != "minecraft:oak_log":
            return -3
    if upper_logs_count >= 2 and leaves_count >= 1:
        return 0
    else:
        return -4
