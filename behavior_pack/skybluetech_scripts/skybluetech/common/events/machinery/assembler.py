# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S

ACTION_PUSH_UPGRADER = 0
ACTION_PULL_UPGRADER = 1


class AssemblerUpgradersUpdate(CustomS2CEvent):
    name = "st:AULU"

    def __init__(self, lis=None):
        # type: (list[tuple[str, str, int]] | None) -> None
        self.lis = lis or []

    def marshal(self):
        return {"lis": self.lis}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["lis"])


class AssemblerActionRequest(MachineryOperationC2S):
    name = "st:APUR"
    extra_attrs = ("action", "index")

    def __init__(self, x, y, z, action, index, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.index = index
        self.player_id = player_id
