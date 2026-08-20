# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S


class ItemSplitterSettingsSetLabel(MachineryOperationC2S):
    name = "st:ISSSL"
    extra_attrs = ("setting_index", "label")

    def __init__(self, x, y, z, setting_index, label, player_id=""):
        # type : (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.label = label
        self.player_id = player_id


class ItemSplitterSettingsSetItem(MachineryOperationC2S):
    name = "st:ISSSI"
    extra_attrs = ("setting_index", "item_id")

    def __init__(self, x, y, z, setting_index, item_id, player_id=""):
        # type : (int, int, int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.item_id = item_id
        self.player_id = player_id


class ItemSplitterSimpleAction(MachineryOperationC2S):
    name = "st:ISSA"
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


class ItemSplitterSettingsListUpdate(CustomS2CEvent):
    name = "st:ISSLU"

    def __init__(self, lis=[]):
        # type: (list[tuple[int, str]]) -> None
        self.lis = lis

    def marshal(self):
        return self.lis

    @classmethod
    def unmarshal(
        cls,
        data,  # type: list[tuple[int, str]]
    ):
        return cls(data)
