from ...internal import ClientComp, ClientLevelId
from ..internal.cacher import MethodCacher

_setOnePopupNotice = MethodCacher(
    lambda: ClientComp.CreateGame(ClientLevelId).SetPopupNotice
)


def SetPopupNotice(message, subtitle="§6提示§f"):
    # type: (str, str) -> None
    _setOnePopupNotice(message, subtitle)


__all__ = ["SetPopupNotice"]
