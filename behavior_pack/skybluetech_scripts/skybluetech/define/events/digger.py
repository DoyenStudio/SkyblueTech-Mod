# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class DiggerWorkModeUpdatedEvent(CustomS2CEvent):
    name = "st:DWMC"

    def __init__(self, x=0, y=0, z=0, active=False):
        # type: (int, int, int, bool) -> None
        self.x = x
        self.y = y
        self.z = z
        self.active = active

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "active": self.active,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            active=data["active"],
        )


class DiggerUpdateCrack(CustomS2CEvent):
    name = "st:DUC"

    def __init__(self, dim=0, x=0, y=0, z=0, level=0):
        # type: (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.level = level

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "level": self.level,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            level=data["level"],
        )