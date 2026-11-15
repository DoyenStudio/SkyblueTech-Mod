# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class AirVentExhaust(CustomS2CEvent):
    name = "st:AirVentExhaust"

    def __init__(self, dim, pos, facing, fluid_id, volume):
        self.dim = dim
        self.pos = tuple(pos)
        self.facing = facing
        self.fluid_id = fluid_id
        self.volume = volume

    def marshal(self):
        return {
            "dim": self.dim, "pos": self.pos, "facing": self.facing,
            "fluid_id": self.fluid_id, "volume": self.volume,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(data["dim"], data["pos"], data["facing"],
                   data["fluid_id"], data["volume"])
