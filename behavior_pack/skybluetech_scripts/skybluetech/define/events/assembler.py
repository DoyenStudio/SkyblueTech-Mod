from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


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

ACTION_PUSH_UPGRADER = 0
ACTION_PULL_UPGRADER = 1


class AssemblerActionRequest(CustomC2SEvent):
    name = "st:APUR"

    def __init__(self, x, y, z, action, index, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.index = index
        self.player_id = player_id

    def marshal(self):
        return {"action": self.action, "index": self.index, "x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["action"],
            data["index"],
            data["__id__"],
        )
