# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class TransmitterSetLabel(CustomC2SEvent):
    name = "st:TmSL"

    def __init__(self, dim=0, x=0, y=0, z=0, facing=0, label=0):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.label = label

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "l": self.label,
        }

    def unmarshal(self, data):
        self.pid = data["__id__"]
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.facing = data["f"]
        self.label = data["l"]


class TransmitterSetPriority(CustomC2SEvent):
    name = "st:TmSP"

    def __init__(self, dim=0, x=0, y=0, z=0, facing=0, priority=0):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.priority = priority

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "p": self.priority,
        }

    def unmarshal(self, data):
        self.pid = data["__id__"]
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.facing = data["f"]
        self.priority = data["p"]