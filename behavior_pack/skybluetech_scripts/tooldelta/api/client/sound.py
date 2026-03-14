# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_playCustomMusic = MethodCacher(
    lambda: CF.CreateCustomAudio(GetLevelId()).PlayCustomMusic
)
_stopCustomMusic = MethodCacher(
    lambda: CF.CreateCustomAudio(GetLevelId()).StopCustomMusic
)
_stopCustomMusicById = MethodCacher(
    lambda: CF.CreateCustomAudio(GetLevelId()).StopCustomMusicById
)


def PlayCustomMusic(
    name,  # type: str
    pos=(0, 0, 0),  # type: tuple[float, float, float]
    volume=1,  # type: float
    pitch=1,  # type: float
    loop=False,  # type: bool
    entity_id=None,  # type: str | None
):
    # type: (...) -> str | int
    return _playCustomMusic(name, pos, volume, pitch, loop, entity_id)


def StopCustomMusic(name, fade_out_time):
    # type: (str, float) -> bool
    return _stopCustomMusic(name, fade_out_time)


def StopCustomMusicById(music_id, fade_out_time):
    # type: (str, float) -> bool
    return _stopCustomMusicById(music_id, fade_out_time)


__all__ = [
    "PlayCustomMusic",
    "StopCustomMusic",
    "StopCustomMusicById",
]
