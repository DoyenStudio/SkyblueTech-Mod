# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S


class FluidSplitterSettingsSetLabel(MachineryOperationC2S):
    name = "st:FSSSL"
    extra_attrs = ("setting_index", "label")

    def __init__(self, dim, x, y, z, setting_index, label, player_id=""):
        # type : (int, int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.label = label
        self.player_id = player_id


class FluidSplitterSettingsSetFluid(MachineryOperationC2S):
    name = "st:FSSSF"
    extra_attrs = ("setting_index", "fluid_id")

    def __init__(self, x, y, z, setting_index, fluid_id, player_id=""):
        # type : (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.fluid_id = fluid_id
        self.player_id = player_id


class FluidSplitterSimpleAction(MachineryOperationC2S):
    name = "st:FSSA"
    extra_attrs = ("action", "extra")

    ACTION_ADD_SETTING = 0
    ACTION_REMOVE_SETTING = 1

    def __init__(self, x, y, z, action, extra, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.action = action
        self.extra = extra
        self.player_id = player_id


class FluidSplitterSettingsListUpdate(CustomS2CEvent):
    name = "st:FSSLU"

    def __init__(self, lis=[]):
        # type: (list[tuple[int, str]]) -> None
        self.lis = lis

    def marshal(self):
        return {"l": self.lis}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            lis=data["l"],
        )
