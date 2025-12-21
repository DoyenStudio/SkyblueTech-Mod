# coding=utf-8

from ..basic import ClientEvent

class OnKeyPressInGame(ClientEvent):
    name = "OnKeyPressInGame"

    screenName = '' # type: str
    """ 当前screenName """
    key = 0 # type: int
    """ 键码，详见KeyBoardType枚举 """
    isDown = 1 # type: int
    """ 是否按下，按下为1，弹起为0 """

    def unmarshal(self, data):
        # type: (dict) -> None
        self.screenName = data["screenName"]
        self.key = int(data["key"])
        self.isDown = int(data["isDown"])

    def marshal(self):
        # type: () -> dict
        return {
            "screenName": self.screenName,
            "key": str(self.key),
            "isDown": str(self.isDown),
        }

