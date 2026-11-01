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

    def __init__(self, lis, dim, x, y, z, revision):
        self.lis = list(lis) if lis is not None else []
        self.pos = (dim, x, y, z)
        self.revision = revision

    def marshal(self):
        # 事件数据只传字典、列表和标量；不能把内部的规则元组交给网络层。
        return {
            "settings": [[label, item_id] for label, item_id in self.lis],
            "pos": list(self.pos),
            "revision": self.revision,
        }

    @classmethod
    def unmarshal(
        cls,
        data,  # type: dict
    ):
        dim, x, y, z = data["pos"]
        return cls(data["settings"], dim, x, y, z, data["revision"])
