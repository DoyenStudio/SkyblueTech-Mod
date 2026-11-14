# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class ShockerCoilSpark(CustomS2CEvent):
    name = "st:ShockerCoilSpark"

    def __init__(self, dim, pos, points):
        self.dim = dim
        self.pos = tuple(pos)
        self.points = points

    def marshal(self):
        return {"dim": self.dim, "pos": self.pos, "points": self.points}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["dim"], data["pos"], data["points"])


class ShockerDischarge(CustomS2CEvent):
    name = "st:ShockerDischarge"

    def __init__(self, dim, first_pos, second_pos, strong, weak_positions, targets=None):
        self.dim = dim
        self.first_pos = tuple(first_pos)
        self.second_pos = tuple(second_pos)
        self.strong = strong
        self.weak_positions = weak_positions
        self.targets = targets or []

    def marshal(self):
        return {
            "dim": self.dim,
            "first_pos": self.first_pos,
            "second_pos": self.second_pos,
            "strong": self.strong,
            "weak_positions": self.weak_positions,
            "targets": self.targets,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"], data["first_pos"], data["second_pos"],
            data["strong"], data["weak_positions"],
            data.get("targets", []),
        )
