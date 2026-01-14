# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class TransmitterSetLabel(CustomC2SEvent):
    name = "st:TmSL"

    def __init__(self, dim, x, y, z, facing, label, pid=""):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.label = label
        self.pid = pid

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "l": self.label,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            facing=data["f"],
            label=data["l"],
            pid=data["__id__"],
        )


class TransmitterSetPriority(CustomC2SEvent):
    name = "st:TmSP"

    def __init__(self, dim, x, y, z, facing, priority, sid=""):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.priority = priority
        self.sid = sid

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "p": self.priority,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            facing=data["f"],
            priority=data["p"],
            sid=data["__id__"],
        )
