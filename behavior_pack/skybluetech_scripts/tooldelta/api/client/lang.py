# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId

CF = GetEngineCompFactory()


def ZHCN(text):
    # type: (str) -> str
    return CF.CreateGame(GetLevelId()).GetChinese(text)
