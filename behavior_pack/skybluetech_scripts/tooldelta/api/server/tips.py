from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_setOnePopupMessage = MethodCacher(
    lambda: CF.CreateGame(GetLevelId()).SetOnePopupNotice
)
_setOneTipMessage = MethodCacher(lambda: CF.CreateGame(GetLevelId()).SetOneTipMessage)
NotifyOneMessage = MethodCacher(lambda: CF.CreateMsg(GetLevelId()).NotifyOneMessage)


def SetOnePopupNotice(playerId, message, subtitle="§6提示§f"):
    # type: (str, str, str) -> None
    _setOnePopupMessage(playerId, message, subtitle)


def SetOneTipMessage(playerId, message):
    # type: (str, str) -> None
    _setOneTipMessage(playerId, message)


__all__ = [
    "SetOnePopupNotice",
    "SetOneTipMessage",
    "NotifyOneMessage",
]
