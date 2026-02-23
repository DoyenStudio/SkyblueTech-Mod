# coding=utf-8

from ...internal import ServerLevelId, ServerComp


def SetCommand(command):
    # type: (str) -> None
    ServerComp.CreateCommand(ServerLevelId).SetCommand(command)


__all__ = ["SetCommand"]
