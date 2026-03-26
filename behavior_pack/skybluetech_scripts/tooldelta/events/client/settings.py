# coding=utf-8

from ..basic import ClientEvent


class OnCustomGamepadChangedEvent(ClientEvent):
    name = "OnCustomGamepadChangedEvent"

    def __init__(
        self,
        name,  # type: str
        oldKey,  # type: str
        newKey,  # type: str
    ):
        self.name = name
        """ 按键名称 """
        self.oldKey = oldKey
        """ 旧的键码 """
        self.newKey = newKey
        """ 新的键码 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            name=data["name"],
            oldKey=data["oldKey"],
            newKey=data["newKey"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "name": self.name,
            "oldKey": self.oldKey,
            "newKey": self.newKey,
        }


class OnCustomGamepadPressInGame(ClientEvent):
    name = "OnCustomGamepadPressInGame"

    def __init__(
        self,
        name,  # type: str
        key,  # type: str
        category,  # type: str
        isDown,  # type: str
        magnitude,  # type: float
        x,  # type: float
        y,  # type: float
        screenName,  # type: str
    ):
        self.name = name
        """ 按键名称 """
        self.key = key
        """ 键码 """
        self.category = category
        """ 按键分类 """
        self.isDown = isDown
        """ 按下状态 ("1"为按下, "0"为抬起)，仅普通按键有效 """
        self.magnitude = magnitude
        """ 扳机力度 (0.0-1.0)，仅扳机键有效 """
        self.x = x
        """ 摇杆X轴偏移 (-1.0-1.0)，仅摇杆键有效 """
        self.y = y
        """ 摇杆Y轴偏移 (-1.0-1.0)，仅摇杆键有效 """
        self.screenName = screenName
        """ 当前屏幕名称 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            name=data["name"],
            key=data["key"],
            category=data["category"],
            isDown=data["isDown"],
            magnitude=data["magnitude"],
            x=data["x"],
            y=data["y"],
            screenName=data["screenName"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "name": self.name,
            "key": self.key,
            "category": self.category,
            "isDown": self.isDown,
            "magnitude": self.magnitude,
            "x": self.x,
            "y": self.y,
            "screenName": self.screenName,
        }


class OnCustomKeyChangedEvent(ClientEvent):
    name = "OnCustomKeyChangedEvent"

    def __init__(
        self,
        name,  # type: str
        oldKey,  # type: str
        newKey,  # type: str
    ):
        self.name = name
        """ 按键名称 """
        self.oldKey = oldKey
        """ 旧的键码 """
        self.newKey = newKey
        """ 新的键码 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            name=data["name"],
            oldKey=data["oldKey"],
            newKey=data["newKey"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "name": self.name,
            "oldKey": self.oldKey,
            "newKey": self.newKey,
        }


class OnCustomKeyPressInGame(ClientEvent):
    name = "OnCustomKeyPressInGame"

    def __init__(
        self,
        name,  # type: str
        key,  # type: str
        category,  # type: str
        isDown,  # type: str
        screenName,  # type: str
    ):
        self.name = name
        """ 按键名称 """
        self.key = key
        """ 键码 """
        self.category = category
        """ 按键分类 """
        self.isDown = isDown
        """ 按下状态 ("1"为按下, "0"为抬起) """
        self.screenName = screenName
        """ 当前屏幕名称 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            name=data["name"],
            key=data["key"],
            category=data["category"],
            isDown=data["isDown"],
            screenName=data["screenName"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "name": self.name,
            "key": self.key,
            "category": self.category,
            "isDown": self.isDown,
            "screenName": self.screenName,
        }
