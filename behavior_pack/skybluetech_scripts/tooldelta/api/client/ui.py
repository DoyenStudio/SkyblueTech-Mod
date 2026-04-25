# coding=utf-8
from mod.client.extraClientApi import (
    GetEngineCompFactory,
    GetMinecraftEnum,
    GetLevelId,
    GetLocalPlayerId,
    GetTouchPos,
)
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()


_getMousePosition = MethodCacher(
    lambda: CF.CreateActorMotion(GetLocalPlayerId()).GetMousePosition
)


def GetFocusPos():
    mouse_data = _getMousePosition()
    if mouse_data is not None:
        return mouse_data
    else:
        return GetTouchPos()


def GetToggleMode():
    """
    返回 0 代表使用鼠标操作, 返回 1 代表使用触摸屏操作
    """
    return CF.CreatePlayerView(GetLocalPlayerId()).GetToggleOption(
        GetMinecraftEnum().OptionId.INPUT_MODE
    )


def GetUIProfile():
    """
    0 表示经典模式, 1 表示携带版模式
    """
    return CF.CreatePlayerView(GetLevelId()).GetUIProfile()


GetScreenSize = MethodCacher(lambda: CF.CreateGame(GetLevelId()).GetScreenSize)

__all__ = [
    "GetFocusPos",
    "GetToggleMode",
    "GetUIProfile",
    "GetScreenSize",
]
