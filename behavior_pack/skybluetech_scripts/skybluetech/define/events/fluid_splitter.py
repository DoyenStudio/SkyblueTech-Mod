# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class FluidSplitterSettingsSetLabel(CustomC2SEvent):
    name = "st:FSSSL"

    def __init__(self, dim=0, x=0, y=0, z=0, setting_index=0, label=0):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.label = label

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "s": self.setting_index,
            "l": self.label,
        }

    def unmarshal(self, data):
        self.pid = data["__id__"]
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.setting_index = data["s"]
        self.label = data["l"]


class FluidSplitterSettingsSetFluid(CustomC2SEvent):
    name = "st:FSSSF"

    def __init__(self, dim=0, x=0, y=0, z=0, setting_index=0, fluid_id=""):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.fluid_id = fluid_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "s": self.setting_index,
            "f": self.fluid_id,
        }

    def unmarshal(self, data):
        self.pid = data["__id__"]
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.setting_index = data["s"]
        self.fluid_id = data["f"]


class FluidSplitterSimpleAction(CustomC2SEvent):
    name = "st:FSSA"

    ACTION_ADD_SETTING = 0
    ACTION_REMOVE_SETTING = 1

    def __init__(self, dim=0, x=0, y=0, z=0, action=0, extra=0):
        # type: (int, int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.extra = extra

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "a": self.action,
            "e": self.extra
        }

    def unmarshal(self, data):
        self.pid = data["__id__"]
        self.dim = data["dim"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.action = data["a"]
        self.extra = data["e"]


class FluidSplitterSettingsListUpdate(CustomS2CEvent):
    name = "st:FSSLU"

    def __init__(self, lis=[]):
        # type: (list[tuple[int, str]]) -> None
        self.lis = lis

    def marshal(self):
        return {"l": self.lis}

    def unmarshal(self, data):
        self.lis = data["l"]
