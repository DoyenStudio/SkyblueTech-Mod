# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId, GetMinecraftEnum

CF = GetEngineCompFactory()


def GetControlMode():
    return CF.CreatePlayerView(GetLevelId()).GetToggleOption(
        GetMinecraftEnum().OptionId.INPUT_MODE
    )


def GetControlModeEnum():
    return GetMinecraftEnum().InputMode


def SetCanMove(enable):
    # type: (bool) -> None
    GetEngineCompFactory().CreateOperation(GetLevelId()).SetCanMove(enable)


__all__ = ["GetControlMode", "GetControlModeEnum", "SetCanMove"]
