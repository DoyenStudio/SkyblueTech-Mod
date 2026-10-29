# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.define import Item

from skybluetech_scripts.tooldelta.events.server import (
    ServerItemUseOnEvent,
    ServerBlockUseEvent,
    BlockRemoveServerEvent,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.tooldelta.utils import nbt
from ...common.define.id_enum.blocks import FAMICOM
from ...common.define.id_enum.items import FamicomCartidges

STATE_MAPPING = {
    FamicomCartidges.YELLOW: 1,
    FamicomCartidges.PURPLE: 2,
    FamicomCartidges.BLUE: 3,
    FamicomCartidges.RED: 4,
    FamicomCartidges.CYAN: 5,
}
K_CARTIDGE_TYPE_STATE = "skybluetech:fc_rom_type"
K_UD_SONG = "song_included"
K_BE_CARTIDGE = "st:cartidge"
K_BE_SONG = "st:song"

rate_limiter = PlayerRateLimiter(0.5)


@ServerBlockUseEvent.Listen()
def onBlockUse(event):
    # type: (ServerBlockUseEvent) -> None
    if event.blockName != FAMICOM:
        return
    if not rate_limiter.record(event.playerId):
        return
    bdata = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(
        event.dimensionId,
        (event.x, event.y, event.z),
    )
    if bdata is None:
        return
    cartidge = bdata[K_BE_CARTIDGE]
    if cartidge is not None:
        removeCartidge(
            event.dimensionId, event.x, event.y, event.z, cartidge, bdata[K_BE_SONG]
        )
        bdata[K_BE_CARTIDGE] = None
        bdata[K_BE_SONG] = None


@ServerItemUseOnEvent.Listen()
def onUseItemOn(event):
    # type: (ServerItemUseOnEvent) -> None
    if event.blockName != FAMICOM:
        return
    bdata = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(
        event.dimensionId,
        (event.x, event.y, event.z),
    )
    if bdata is None:
        return
    x = event.x
    y = event.y
    z = event.z
    cartidge = bdata[K_BE_CARTIDGE]
    if cartidge is not None:
        removeCartidge(event.dimensionId, x, y, z, cartidge, bdata[K_BE_SONG])
        bdata[K_BE_CARTIDGE] = None
        bdata[K_BE_SONG] = None
        return
    item = event.item
    state = STATE_MAPPING.get(item.id)
    if state is None:
        return
    song = nbt.GetValueWithDefault(item.userData or {}, K_UD_SONG, None)
    if song is None:
        return
    bdata[K_BE_CARTIDGE] = item.id
    bdata[K_BE_SONG] = song
    _block_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates((x, y, z), event.dimensionId)
    if _block_states is not None:
        _block_states.update({K_CARTIDGE_TYPE_STATE: state})
        CF.CreateBlockState(LEVEL_ID).SetBlockStates((x, y, z), _block_states, event.dimensionId)
    CF.CreateCommand(LEVEL_ID).SetCommand(
        "/execute positioned %d %d %d run playsound %s @a[r=30]" % (x, y, z, song),
        event.entityId,
    )
    CF.CreateItem(event.entityId).SpawnItemToPlayerCarried(
        Item("minecraft:air").marshal(),
        event.entityId,
    )


def removeCartidge(dim, x, y, z, cartidge, song):
    # type: (int, int, int, int, str, str | None) -> None
    GetServer().CreateEngineItemEntity(Item(cartidge).marshal(), dim, (x + 0.5, y, z + 0.5))
    _block_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates((x, y, z), dim)
    if _block_states is not None:
        _block_states.update({K_CARTIDGE_TYPE_STATE: 0})
        CF.CreateBlockState(LEVEL_ID).SetBlockStates((x, y, z), _block_states, dim)
    if song is not None:
        CF.CreateCommand(LEVEL_ID).SetCommand("/stopsound @a[r=30] %s" % song, None)


@BlockRemoveServerEvent.Listen()
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if event.fullName != FAMICOM:
        return
    bdata = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(
        event.dimension,
        (event.x, event.y, event.z),
    )
    if bdata is None:
        return
    cartidge = bdata[K_BE_CARTIDGE]
    if cartidge is not None:
        removeCartidge(
            event.dimension, event.x, event.y, event.z, cartidge, bdata[K_BE_SONG]
        )
