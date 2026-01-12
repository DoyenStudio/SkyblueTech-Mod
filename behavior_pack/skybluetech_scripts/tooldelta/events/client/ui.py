# coding=utf-8

from ..basic import ClientEvent


class UiInitFinishedEvent(ClientEvent):
    name = "UiInitFinished"

    @classmethod
    def unmarshal(cls, _):
        return cls()


class GridComponentSizeChangedClientEvent(ClientEvent):
    name = "GridComponentSizeChangedClientEvent"

    path = '' # type: str
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
