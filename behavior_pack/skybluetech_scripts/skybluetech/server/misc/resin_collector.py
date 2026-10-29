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
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from ...common.define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM
from ...common.define.id_enum import RESIN_COLLECTOR, Machinery
from ...common.define.id_enum.items import RESIN, RESIN_SPOON


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
    facing = FACING_EN2NUM[blockstates["minecraft:cardinal_direction"]]
    dx, dz = FACING_DXZ[facing - 2]
    res = log_is_in_tree(
        event.dimensionId, event.posX + dx, event.posY, event.posZ + dz
    )
    if res != 0:
        return
    resin_storage = blockstates["skybluetech:resin_storage"]
    if resin_storage >= 6:
        return
    blockstates.update({"skybluetech:resin_storage": resin_storage + 1})
    CF.CreateBlockState(LEVEL_ID).SetBlockStates(
        (event.posX, event.posY, event.posZ),
        blockstates,
        event.dimensionId,
    )


@ServerItemUseOnEvent.ListenWithUserData()
def onItemUseOnEvent(event):
    # type: (ServerItemUseOnEvent) -> None
    if event.item.id != RESIN_SPOON or event.blockName != RESIN_COLLECTOR:
        return
    collector_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
        (event.x, event.y, event.z),
        event.dimensionId,
    )
    resin_store = collector_states["skybluetech:resin_storage"]
    if resin_store <= 0:
        return
    durability = event.item.durability or event.item.GetBasicInfo().maxDurability
    durability -= 1
    event.item.durability = durability
    collector_states.update({"skybluetech:resin_storage": resin_store - 1})
    CF.CreateBlockState(LEVEL_ID).SetBlockStates(
        (event.x, event.y, event.z),
        collector_states,
        event.dimensionId,
    )
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
        disconnect = False
        if event.toBlockName == Machinery.RESIN_COLLECTOR_OUTPUTER:
            prev_facing = FACING_EN2NUM[
                CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(
                    Machinery.RESIN_COLLECTOR_OUTPUTER,
                    event.fromBlockAuxValue,
                )["minecraft:cardinal_direction"]
            ]
            current_facing = FACING_EN2NUM[
                CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(
                    Machinery.RESIN_COLLECTOR_OUTPUTER,
                    event.toAuxValue,
                )["minecraft:cardinal_direction"]
            ]
            dx, dz = FACING_DXZ[prev_facing - 2]
            dx2, dz2 = FACING_DXZ[current_facing - 2]
            # 原连接到此树脂采集斗的树脂输出器被诸如机械动力扳手这样的东西调整方向
            disconnect = (
                event.neighborPosX + dx == event.posX
                and event.neighborPosZ + dz == event.posZ
            ) and (
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
