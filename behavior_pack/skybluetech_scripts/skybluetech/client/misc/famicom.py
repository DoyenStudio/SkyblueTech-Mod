# coding=utf-8
import time
from skybluetech_scripts.tooldelta.api.client import (
    PlayCustomMusic,
    StopCustomMusicById,
    SetPopupNotice,
)
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
)
from ...common.define.id_enum.blocks import FAMICOM
from ...common.events.misc.famicom import FamicomPlaySoundEvent

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
            SetPopupNotice("§c无法播放卡带音乐", "§c错误")


last_used_time = 0


@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    global last_used_time
    if event.blockName != FAMICOM:
        return
    nowtime = time.time()
    if nowtime - last_used_time < 0.5:
        event.cancel()
        return
    last_used_time = nowtime
