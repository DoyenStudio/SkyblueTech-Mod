# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent

MODE_LOAD = 0
MODE_UNLOAD = 1


class HydroponicBedClientLoadEvent(CustomC2SEvent):
    name = "st:HBCLE"

    def __init__(self, dim, x, y, z, mode, player_id=""):
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode
        self.player_id = player_id

    def marshal(self):
        return {"d": self.dim, "x": self.x, "y": self.y, "z": self.z, "m": self.mode}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["d"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            mode=data["m"],
            player_id=data["__id__"]
        )


class HydroponicBedModelUpdateEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, x, y, z, crop_id, aux):
        # type: (int, int, int, str | None, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.crop_id = crop_id
        self.aux = aux

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "c": self.crop_id, "a": self.aux}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            crop_id=data["c"],
            aux=data["a"]
        )


class HydroponicBedModelUpdatesEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, updates=[]):
        # type: (list[tuple[int, int, int, str, int]]) -> None
        self.updates = updates

    def marshal(self):
        return self.updates

    @classmethod
    def unmarshal(
        cls,
        data # type: list[tuple[int, int, int, str, int]]
    ):
        return cls(data)
