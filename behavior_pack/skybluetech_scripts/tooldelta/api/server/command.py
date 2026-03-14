# coding=utf-8
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId

CF = GetEngineCompFactory()


def SetCommand(command, entity_id=None):
    # type: (str, str | None) -> None
    CF.CreateCommand(GetLevelId()).SetCommand(command, entity_id)


__all__ = ["SetCommand"]
