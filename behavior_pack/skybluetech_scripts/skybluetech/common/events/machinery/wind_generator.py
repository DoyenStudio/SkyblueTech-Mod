# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent
from .basic import MachineryOperationC2S


class WindGeneratorStatesRequest(MachineryOperationC2S):
    name = "st:WGSR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id


class WindGeneratorStatesUpdate(CustomS2CEvent):
    name = "st:WGSU"

    PADDLE_EMPTY = 0
    PADDLE_IRON = 1
    PADDLE_STEEL = 2

    def __init__(self, x, y, z, paddle_type, rot_speed):
        # type: (int, int, int, int | None, float) -> None
        self.x = x
        self.y = y
        self.z = z
        self.paddle_type = paddle_type
        self.rot_speed = rot_speed

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pt": self.paddle_type,
            "rs": self.rot_speed,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            paddle_type=data["pt"],
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
