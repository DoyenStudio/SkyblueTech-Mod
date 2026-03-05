# coding=utf-8

from ...internal import ServerLevelId, ServerComp


def SetCommand(command, entity_id=None):
    # type: (str, str | None) -> None
    ServerComp.CreateCommand(ServerLevelId).SetCommand(command, entity_id)


__all__ = ["SetCommand"]
