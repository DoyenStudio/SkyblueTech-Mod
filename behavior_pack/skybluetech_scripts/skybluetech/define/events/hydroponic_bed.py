# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent

MODE_LOAD = 0
MODE_UNLOAD = 1


class HydroponicBedClientLoadEvent(CustomC2SEvent):
    name = "st:HBCLE"

    def __init__(self, dim=0, x=0, y=0, z=0, mode=0):
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode

    def marshal(self):
        return {"d": self.dim, "x": self.x, "y": self.y, "z": self.z, "m": self.mode}

    def unmarshal(self, data):
        self.player_id = data["__id__"]
        self.dim = data["d"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.mode = data["m"]


class HydroponicBedModelUpdateEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, x=0, y=0, z=0, crop_id="", aux=0):
        # type: (int, int, int, str | None, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.crop_id = crop_id
        self.aux = aux

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "c": self.crop_id, "a": self.aux}

    def unmarshal(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.crop_id = data["c"]
        self.aux = data["a"]


class HydroponicBedModelUpdatesEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, updates=[]):
        # type: (list[tuple[int, int, int, str, int]]) -> None
        self.updates = updates

    def marshal(self):
        return {"u": self.updates}

    def unmarshal(self, data):
        self.updates = data["u"]

