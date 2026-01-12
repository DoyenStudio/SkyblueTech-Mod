# coding=utf-8

from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class ItemSplitterSettingsSetLabel(CustomC2SEvent):
    name = "st:ISSSL"

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

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.pid = data["__id__"]
        instance.dim = data["dim"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.setting_index = data["s"]
        instance.label = data["l"]
        return instance


class ItemSplitterSettingsSetItem(CustomC2SEvent):
    name = "st:ISSSI"

    def __init__(self, dim=0, x=0, y=0, z=0, setting_index=0, item_id=""):
        # type : (int, int, int, int, int) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.setting_index = setting_index
        self.item_id = item_id

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
        instance = cls()
        instance.pid = data["__id__"]
        instance.dim = data["dim"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.setting_index = data["s"]
        instance.item_id = data["f"]
        return instance


class ItemSplitterSimpleAction(CustomC2SEvent):
    name = "st:ISSA"

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

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.pid = data["__id__"]
        instance.dim = data["dim"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.action = data["a"]
        instance.extra = data["e"]
        return instance


class ItemSplitterSettingsListUpdate(CustomS2CEvent):
    name = "st:ISSLU"

    def __init__(self, lis=[]):
        # type: (list[tuple[int, str]]) -> None
        self.lis = lis

    def marshal(self):
        return {"l": self.lis}

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.lis = data["l"]
        return instance
