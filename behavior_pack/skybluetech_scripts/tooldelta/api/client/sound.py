# coding=utf-8
#

from ...internal import ClientComp, ClientLevelId
from ..internal.cacher import MethodCacher

_playCustomMusic = MethodCacher(lambda :ClientComp.CreateCustomAudio(ClientLevelId).PlayCustomMusic)
_stopCustomMusic = MethodCacher(lambda :ClientComp.CreateCustomAudio(ClientLevelId).StopCustomMusic)
_stopCustomMusicById = MethodCacher(lambda :ClientComp.CreateCustomAudio(ClientLevelId).StopCustomMusicById)

def PlayCustomMusic(
    name, # type: str
    pos=(0, 0, 0), # type: tuple[float, float, float]
    volume=1, # type: float
    pitch=1, # type: float
    loop=False, # type: bool
    entity_id=None, # type: str | None
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
    'PlayCustomMusic',
    'StopCustomMusic',
    'StopCustomMusicById',
]
