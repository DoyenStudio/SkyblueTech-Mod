# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class EffluentOutfallDischarge(CustomS2CEvent):
    name = "st:EffluentOutfallDischarge"

    def __init__(self, dim, pos, fluid_id):
        self.dim = dim
        self.pos = tuple(pos)
        self.fluid_id = fluid_id

    def marshal(self):
        return {"dim": self.dim, "pos": self.pos, "fluid_id": self.fluid_id}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["dim"], data["pos"], data["fluid_id"])
