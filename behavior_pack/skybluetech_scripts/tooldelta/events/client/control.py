# coding=utf-8

from ..basic import ClientEvent
from mod.client.extraClientApi import GetMinecraftEnum as _GetMinecraftEnum

_KeyBoardType = _GetMinecraftEnum().KeyBoardType


class OnKeyPressInGame(ClientEvent):
    name = "OnKeyPressInGame"

    KeyBoardType = _KeyBoardType

    screenName = '' # type: str
    """ 当前screenName """
    key = 0 # type: int
    """ 键码，详见KeyBoardType枚举 """
    isDown = 1 # type: int
    """ 是否按下，按下为1，弹起为0 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> OnKeyPressInGame
        instance = cls()
        instance.screenName = data["screenName"]
        instance.key = int(data["key"])
        instance.isDown = int(data["isDown"])
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "screenName": self.screenName,
            "key": str(self.key),
            "isDown": str(self.isDown),
        }

