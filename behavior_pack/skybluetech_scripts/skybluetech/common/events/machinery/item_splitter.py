# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class ItemSplitterSettingsSetLabel(CustomC2SEvent):
    name = "st:ISSSL"

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


class ItemSplitterSettingsSetItem(CustomC2SEvent):
    name = "st:ISSSI"

    def __init__(self, dim, x, y, z, setting_index, item_id, player_id=""):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.item_id = item_id
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "s": self.setting_index,
            "f": self.item_id,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            setting_index=data["s"],
            item_id=data["f"],
            player_id=data["__id__"],
        )


class ItemSplitterSimpleAction(CustomC2SEvent):
    name = "st:ISSA"

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
        data # type: list[tuple[int, str]]
    ):
        return cls(data)
