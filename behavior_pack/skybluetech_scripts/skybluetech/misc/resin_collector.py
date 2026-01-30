# coding=utf-8
import random
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.timer import ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockStates,
    GetBlockName,
    UpdateBlockStates,
    SpawnItemToPlayerCarried,
    SpawnDroppedItem,
    SetBlock,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockRandomTickServerEvent,
    ServerEntityTryPlaceBlockEvent,
    BlockNeighborChangedServerEvent,
    ServerItemUseOnEvent,
)
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.extensions.player_rate_limit import PlayerRateLimiter
from ..define.id_enum.blocks import RESIN_COLLECTOR
from ..define.id_enum.items import RESIN, RESIN_SPOON
from ..define.facing import FACING_DXZ, FACING_EN, FACING_EN2NUM

# SERVER PART


@ServerEntityTryPlaceBlockEvent.Listen()
def onBlockPlace(event):
    # type: (ServerEntityTryPlaceBlockEvent) -> None
    if event.fullName != RESIN_COLLECTOR:
        return
    for i, (dx, dz) in enumerate(FACING_DXZ):
        nblock_id = GetBlockName(
            event.dimensionId, (event.x + dx, event.y, event.z + dz)
        )
        if nblock_id != "minecraft:oak_log":
            continue
        ExecLater(
            0,
            lambda: UpdateBlockStates(
                event.dimensionId,
                (event.x, event.y, event.z),
                {"minecraft:cardinal_direction": FACING_EN[i + 2]},
            ),
        )
        return
    event.cancel()


@BlockRandomTickServerEvent.Listen()
def onBlockRandomTick(event):
    # type: (BlockRandomTickServerEvent) -> None
    if event.fullName != RESIN_COLLECTOR:
        return
    if random.random() < 0.75:
        return
    blockstates = GetBlockStates(
        event.dimensionId, (event.posX, event.posY, event.posZ)
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
    UpdateBlockStates(
        event.dimensionId,
        (event.posX, event.posY, event.posZ),
        {"skybluetech:resin_storage": resin_storage + 1},
        blockstates,
    )


@ServerItemUseOnEvent.ListenWithUserData()
def onItemUseOnEvent(event):
    # type: (ServerItemUseOnEvent) -> None
    if event.item.id != RESIN_SPOON or event.blockName != RESIN_COLLECTOR:
        return
    collector_states = GetBlockStates(event.dimensionId, (event.x, event.y, event.z))
    resin_store = collector_states["skybluetech:resin_storage"]
    if resin_store <= 0:
        return
    durability = event.item.durability or event.item.GetBasicInfo().maxDurability
    durability -= 1
    event.item.durability = durability
    UpdateBlockStates(
        event.dimensionId,
        (event.x, event.y, event.z),
        {"skybluetech:resin_storage": resin_store - 1},
        collector_states,
    )
    if event.item.durability == 0:
        SpawnItemToPlayerCarried(event.entityId, Item("minecraft:air"))
    else:
        SpawnItemToPlayerCarried(event.entityId, event.item)
    SpawnDroppedItem(event.dimensionId, (event.x + 0.5, event.y + 0.5, event.z + 0.5), Item(RESIN))



@BlockNeighborChangedServerEvent.Listen()
def onNeighborChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if (
        event.blockName == RESIN_COLLECTOR
        and event.fromBlockName == "minecraft:oak_log"
    ):
        blockstates = GetBlockStates(
            event.dimensionId, (event.posX, event.posY, event.posZ)
        )
        facing = FACING_EN2NUM[blockstates["minecraft:cardinal_direction"]]
        dx, dz = FACING_DXZ[facing - 2]
        if (
            event.posX + dx == event.neighborPosX
            and event.posZ + dz == event.neighborPosZ
            and event.posY == event.neighborPosY
        ):
            SetBlock(
                event.dimensionId,
                (event.posX, event.posY, event.posZ),
                "minecraft:air",
                old_block_handing=1,
            )
        resin_drop = blockstates["skybluetech:resin_storage"] // 2
        SpawnDroppedItem(
            event.dimensionId,
            (event.posX + 0.5, event.posY + 0.5, event.posZ + 0.5),
            Item(RESIN, count=resin_drop)
        )


def log_is_in_tree(dim, x, y, z):
    # type: (int, int, int, int) -> int
    upper_logs_count = 0
    leaves_count = 0
    if GetBlockName(dim, (x, y - 1, z)) != "minecraft:oak_log":
        return -1
    for _y in range(y, y + 8):
        block_id = GetBlockName(dim, (x, _y, z))
        if block_id == "minecraft:oak_log":
            upper_logs_count += 1
        elif block_id == "minecraft:oak_leaves":
            leaves_count += 1
        else:
            break
    for _y in range(y - 2, y - 6, -1):
        block_id = GetBlockName(dim, (x, _y, z))
        if block_id == "minecraft:dirt" or block_id == "minecraft:grass_block":
            break
        elif block_id != "minecraft:oak_log":
            return -3
    if upper_logs_count >= 2 and leaves_count >= 1:
        return 0
    else:
        return -4


# CLIENT PART

limiter = PlayerRateLimiter(0.2)


@ClientBlockUseEvent.Listen()
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName == RESIN_COLLECTOR:
        if not limiter.record(event.playerId):
            event.cancel()
