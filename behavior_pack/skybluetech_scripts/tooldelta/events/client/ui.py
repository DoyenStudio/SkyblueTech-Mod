# coding=utf-8

from ..basic import ClientEvent


class UiInitFinishedEvent(ClientEvent):
    name = "UiInitFinished"

    @classmethod
    def unmarshal(cls, _):
        return cls()


class GridComponentSizeChangedClientEvent(ClientEvent):
    name = "GridComponentSizeChangedClientEvent"

    path = ""  # type: str
    """ grid网格所在的路径（从UI根节点算起） """

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.path = data["path"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "path": self.path,
        }


class ScreenSizeChangedClientEvent(ClientEvent):
    name = "ScreenSizeChangedClientEvent"

    def __init__(
        self,
        beforeX,  # type: float
        beforeY,  # type: float
        afterX,  # type: float
        afterY,  # type: float
    ):
        self.beforeX = beforeX
        """ 屏幕大小改变前的宽度 """
        self.beforeY = beforeY
        """ 屏幕大小改变前的高度 """
        self.afterX = afterX
        """ 屏幕大小改变后的宽度 """
        self.afterY = afterY
        """ 屏幕大小改变后的高度 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            beforeX=data["beforeX"],
            beforeY=data["beforeY"],
            afterX=data["afterX"],
            afterY=data["afterY"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "beforeX": self.beforeX,
            "beforeY": self.beforeY,
            "afterX": self.afterX,
            "afterY": self.afterY,
        }
