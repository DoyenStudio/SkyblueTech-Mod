# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class TransmitterSwitchAccessMode(CustomC2SEvent):
    name = "st:TmSAM"

    def __init__(self, x, y, z, transmitter_type, facing, pid=""):
        # type: (int, int, int, int | str, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.transmitter_type = transmitter_type
        self.facing = facing
        self.pid = pid

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "t": self.transmitter_type,
            "f": self.facing,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            transmitter_type=data["t"],
            facing=data["f"],
            pid=data["__id__"],
        )


class TransmitterSetLabel(CustomC2SEvent):
    name = "st:TmSL"

    def __init__(self, x, y, z, facing, label, pid=""):
        # type : (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.label = label
        self.pid = pid

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "l": self.label,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            facing=data["f"],
            label=data["l"],
            pid=data["__id__"],
        )


class TransmitterSetPriority(CustomC2SEvent):
    name = "st:TmSP"

    def __init__(self, x, y, z, facing, priority, pid=""):
        # type : (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.facing = facing
        self.priority = priority
        self.pid = pid

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "f": self.facing,
            "p": self.priority,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            facing=data["f"],
            priority=data["p"],
            pid=data["__id__"],
        )
