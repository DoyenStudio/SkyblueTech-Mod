# coding=utf-8
import mod.client.extraClientApi as clientApi
from ...internal import ClientComp, ClientLevelId, GetClient
from ..internal.cacher import MethodCacher


def GetControlMode():
    return ClientComp.CreatePlayerView(ClientLevelId).GetToggleOption(
        clientApi.GetMinecraftEnum().OptionId.INPUT_MODE
    )


def GetControlModeEnum():
    return clientApi.GetMinecraftEnum().InputMode


def SetCanMove(enable):
    # type: (bool) -> None
    clientApi.GetEngineCompFactory().CreateOperation(ClientLevelId).SetCanMove(enable)


__all__ = ["GetControlMode", "GetControlModeEnum", "SetCanMove"]
