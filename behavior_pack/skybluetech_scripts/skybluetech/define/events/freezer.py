from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class FreezerModeChangedEvent(CustomC2SEvent):
    name = "st:FreezerModeChanged"

    def __init__(self, dim, x, y, z, new_mode, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.new_mode = new_mode
        self.player_id = player_id

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
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            new_mode=data["new_mode"],
            player_id=data["__id__"]
        )
