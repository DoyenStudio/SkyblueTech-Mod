# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId

CF = GetEngineCompFactory()


def GetConfigData(
    key,  # type: str
    is_global=False,  # type: bool
):
    return CF.CreateConfigClient(GetLevelId()).GetConfigData(key, is_global)


def SetConfigData(
    key,  # type: str
    value,
    is_global=False,  # type: bool
):
    return CF.CreateConfigClient(GetLevelId()).SetConfigData(key, value, is_global)
