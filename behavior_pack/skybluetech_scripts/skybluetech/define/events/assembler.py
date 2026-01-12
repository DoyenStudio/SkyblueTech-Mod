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
        instance = cls()
        instance.lis = data["lis"]
        return instance

ACTION_PUSH_UPGRADER = 0
ACTION_PULL_UPGRADER = 1


class AssemblerActionRequest(CustomC2SEvent):
    name = "st:APUR"

    def __init__(self, x=0, y=0, z=0, action=-1, index=-1):
        # type: (int, int, int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.index = index

    def marshal(self):
        return {"action": self.action, "index": self.index, "x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.action = data["action"]
        instance.index = data["index"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.pid = data["__id__"]
        return instance
