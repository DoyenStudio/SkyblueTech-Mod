from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_setOnePopupNotice = MethodCacher(lambda: CF.CreateGame(GetLevelId()).SetPopupNotice)


def SetPopupNotice(message, subtitle="§6提示§f"):
    # type: (str, str) -> None
    _setOnePopupNotice(message, subtitle)


__all__ = ["SetPopupNotice"]
