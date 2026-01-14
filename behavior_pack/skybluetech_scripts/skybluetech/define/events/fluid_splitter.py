# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class FluidSplitterSettingsSetLabel(CustomC2SEvent):
    name = "st:FSSSL"

    def __init__(self, dim, x, y, z, setting_index, label, player_id=""):
        # type : (int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.label = label
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "s": self.setting_index,
            "l": self.label,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            setting_index=data["s"],
            label=data["l"],
            player_id=data["__id__"],
        )


class FluidSplitterSettingsSetFluid(CustomC2SEvent):
    name = "st:FSSSF"

    def __init__(self, dim, x, y, z, setting_index, fluid_id, player_id=""):
        # type : (int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.fluid_id = fluid_id
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "s": self.setting_index,
            "f": self.fluid_id,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            setting_index=data["s"],
            fluid_id=data["f"],
            player_id=data["__id__"],
        )


class FluidSplitterSimpleAction(CustomC2SEvent):
    name = "st:FSSA"

    ACTION_ADD_SETTING = 0
    ACTION_REMOVE_SETTING = 1

    def __init__(self, dim, x, y, z, action, extra, player_id=""):
        # type: (int, int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.extra = extra
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "a": self.action,
            "e": self.extra
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            action=data["a"],
            extra=data["e"],
            player_id=data["__id__"],
        )


class FluidSplitterSettingsListUpdate(CustomS2CEvent):
    name = "st:FSSLU"

    def __init__(self, lis=[], player_id=""):
        # type: (list[tuple[int, str]], str) -> None
        self.lis = lis
        self.player_id = player_id

    def marshal(self):
        return {"l": self.lis}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            lis=data["l"],
            player_id=data["__id__"],
        )
