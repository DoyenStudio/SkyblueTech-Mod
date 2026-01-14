# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class WindGeneratorStatesRequest(CustomC2SEvent):
    name = "st:WGSR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            player_id=data["__id__"],
        )


class WindGeneratorStatesUpdate(CustomS2CEvent):
    name = "st:WGSU"

    def __init__(self, x, y, z, rot_speed):
        # type: (int, int, int, float) -> None
        self.x = x
        self.y = y
        self.z = z
        self.rot_speed = rot_speed

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rs": self.rot_speed,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            rot_speed=data["rs"],
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
