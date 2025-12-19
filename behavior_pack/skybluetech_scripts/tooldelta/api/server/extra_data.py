# coding=utf-8
from ...internal import ServerComp

if 0:
    from typing import TypeVar
    T = TypeVar('T')

def GetExtraData(
    entity_id, # type: str
    key, # type: str
    default=None, # type: T
):
    # type: (...) -> T
    res = ServerComp.CreateExtraData(entity_id).GetExtraData(key)
    if res is None:
        return default
    return res

def SetExtraData(
    entity_id, # type: str
    key, # type: str
    value,
    auto_save=True,
):
    return ServerComp.CreateExtraData(entity_id).SetExtraData(key, value, auto_save)