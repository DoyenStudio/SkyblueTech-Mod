from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class ElectricHeaterSetPowerEvent(CustomC2SEvent):
    name = "st:EHS"

    def __init__(self, dim, x, y, z, power, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.power = power
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "power": self.power
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            power=data["power"],
            player_id=data["__id__"],
        )
