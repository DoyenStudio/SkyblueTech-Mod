from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class ElectricHeaterSetPowerEvent(CustomC2SEvent):
    name = "st:EHS"

    def __init__(self, dim=0, x=0, y=0, z=0, power=0):
        # type: (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.power = power

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
        instance = cls()
        instance.dim = data["dim"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.power = data["power"]
        instance.player_id = data["__id__"]
        return instance
