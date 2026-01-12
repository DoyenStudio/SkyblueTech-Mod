from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class FreezerModeChangedEvent(CustomC2SEvent):
    name = "st:FreezerModeChanged"

    def __init__(self, dim=0, x=0, y=0, z=0, new_mode=0):
        # type: (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.new_mode = new_mode

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "new_mode": self.new_mode
        }

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.dim = data["dim"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.new_mode = data["new_mode"]
        instance.player_id = data["__id__"]
        return instance
