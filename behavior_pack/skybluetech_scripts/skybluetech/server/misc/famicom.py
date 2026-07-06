# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockEntityData,
    SpawnDroppedItem,
    SetCommand,
    UpdateBlockStates,
    SpawnItemToPlayerCarried,
)
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
    bdata = GetBlockEntityData(event.dimensionId, (event.x, event.y, event.z))
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
    bdata = GetBlockEntityData(event.dimensionId, (event.x, event.y, event.z))
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
    UpdateBlockStates(
        event.dimensionId,
        (x, y, z),
        {K_CARTIDGE_TYPE_STATE: state},
    )
    SetCommand("/playsound %s @a[r=30] %d %d %d" % (song, x, y, z))
    SpawnItemToPlayerCarried(event.entityId, Item("minecraft:air"))


def removeCartidge(dim, x, y, z, cartidge, song):
    # type: (int, int, int, int, str, str | None) -> None
    SpawnDroppedItem(dim, (x + 0.5, y, z + 0.5), Item(cartidge))
    UpdateBlockStates(dim, (x, y, z), {K_CARTIDGE_TYPE_STATE: 0})
    if song is not None:
        SetCommand("/stopsound @a[r=30] %s" % song)


@BlockRemoveServerEvent.Listen()
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if event.fullName != FAMICOM:
        return
    bdata = GetBlockEntityData(event.dimension, (event.x, event.y, event.z))
    if bdata is None:
        return
    cartidge = bdata[K_BE_CARTIDGE]
    if cartidge is not None:
        removeCartidge(
            event.dimension, event.x, event.y, event.z, cartidge, bdata[K_BE_SONG]
        )
