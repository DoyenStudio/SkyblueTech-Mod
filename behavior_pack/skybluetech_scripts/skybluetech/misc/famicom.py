# coding=utf-8
import time
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client import (
    PlayCustomMusic,
    StopCustomMusicById,
    GetLocalPlayerId
)
from skybluetech_scripts.tooldelta.api.server import (
    GetPlayersInDim,
    GetPos,
    GetBlockEntityData,
    SpawnDroppedItem,
    SetOnePopupNotice,
    UpdateBlockStates,
    SpawnItemToPlayerCarried,
)
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.events.server import (
    ServerItemUseOnEvent,
    ServerBlockUseEvent,
    BlockRemoveServerEvent,
)
from skybluetech_scripts.tooldelta.events.notify import NotifyToClients

FAMICOM_ID = "skybluetech:famicom"
MUSIC_MAPPING = {
    "skybluetech:famicom_cartidge_1": "music.skybluetech.famicom_1",
    "skybluetech:famicom_cartidge_2": "music.skybluetech.famicom_2",
    "skybluetech:famicom_cartidge_3": "music.skybluetech.famicom_3",
}
STATE_MAPPING = {
    "skybluetech:famicom_cartidge_1": 1,
    "skybluetech:famicom_cartidge_2": 2,
    "skybluetech:famicom_cartidge_3": 3,
}
K_CARTIDGE_TYPE_STATE = "skybluetech:fc_rom_type"


class FamicomPlaySoundEvent(CustomS2CEvent):
    name = "st:FCPlaysound"

    def __init__(self, dim=0, x=0, y=0, z=0, sound_name="", stop=False):
        # type: (int, float, float, float, str, bool) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.sound_name = sound_name
        self.stop = stop

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "sound_name": self.sound_name,
            "stop": self.stop,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            sound_name=data["sound_name"],
            stop=data["stop"],
        )


@ServerBlockUseEvent.Listen()
def onBlockUse(event):
    # type: (ServerBlockUseEvent) -> None
    if event.blockName != FAMICOM_ID:
        return
    bdata = GetBlockEntityData(event.dimensionId, event.x, event.y, event.z)
    if bdata is None:
        return
    x = event.x
    y = event.y
    z = event.z
    cartidge = bdata["st:cartidge"]
    if cartidge is not None:
        removeCartidge(event.dimensionId, x, y, z, cartidge)
        bdata["st:cartidge"] = None


@ServerItemUseOnEvent.Listen()
def onUseItemOn(event):
    # type: (ServerItemUseOnEvent) -> None
    if event.blockName != FAMICOM_ID:
        return
    bdata = GetBlockEntityData(event.dimensionId, event.x, event.y, event.z)
    if bdata is None:
        return
    x = event.x
    y = event.y
    z = event.z
    cartidge = bdata["st:cartidge"]
    if cartidge is not None:
        removeCartidge(event.dimensionId, x, y, z, cartidge)
        bdata["st:cartidge"] = None
        return
    item = event.item
    music_mapping = MUSIC_MAPPING.get(item.id)
    if music_mapping is None:
        return
    inrange_players = [
        i
        for i in GetPlayersInDim(event.dimensionId)
        if all(abs(b - a) <= 32 for a, b in zip(GetPos(i), (x, y, z)))
    ]
    bdata["st:cartidge"] = item.id
    UpdateBlockStates(
        event.dimensionId,
        (x, y, z),
        {K_CARTIDGE_TYPE_STATE: STATE_MAPPING[item.id]},
    )
    NotifyToClients(
        inrange_players,
        FamicomPlaySoundEvent(event.dimensionId, x, y, z, music_mapping),
    )
    SpawnItemToPlayerCarried(event.entityId, Item("minecraft:air"))


def removeCartidge(dim, x, y, z, cartidge):
    # type: (int, int, int, int, str) -> None
    SpawnDroppedItem(dim, (x + 0.5, y, z + 0.5), Item(cartidge))
    music_mapping = MUSIC_MAPPING.get(cartidge)
    if music_mapping is None:
        return
    UpdateBlockStates(dim, (x, y, z), {K_CARTIDGE_TYPE_STATE: 0})
    inrange_players = [
        i
        for i in GetPlayersInDim(dim)
        if all(abs(b - a) <= 32 for a, b in zip(GetPos(i), (x, y, z)))
    ]
    NotifyToClients(
        inrange_players, FamicomPlaySoundEvent(dim, x, y, z, music_mapping, True)
    )


client_music_ids = {}  # type: dict[str, str]


@FamicomPlaySoundEvent.Listen()
def onFamicomPlaySoundEvent(event):
    # type: (FamicomPlaySoundEvent) -> None
    if event.stop:
        audio_id = client_music_ids.pop(event.sound_name, None)
        if audio_id is not None:
            StopCustomMusicById(audio_id, 0)
    else:
        audio_id = PlayCustomMusic(
            event.sound_name,
            (event.x, event.y, event.z),
            1,
            1,
            True,
            None,
        )
        if isinstance(audio_id, str):
            client_music_ids[event.sound_name] = audio_id
        else:
            SetOnePopupNotice(
                GetLocalPlayerId(), "§c无法播放 FC 音乐: {}".format(audio_id)
            )

@BlockRemoveServerEvent.Listen()
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if event.fullName != FAMICOM_ID:
        return
    bdata = GetBlockEntityData(event.dimension, event.x, event.y, event.z)
    if bdata is None:
        return
    x = event.x
    y = event.y
    z = event.z
    cartidge = bdata["st:cartidge"]
    if cartidge is not None:
        removeCartidge(event.dimension, x, y, z, cartidge)


last_used_time = 0


@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    global last_used_time
    if event.blockName != FAMICOM_ID:
        return
    nowtime = time.time()
    if nowtime - last_used_time < 0.5:
        event.cancel()
        return
    last_used_time = nowtime
