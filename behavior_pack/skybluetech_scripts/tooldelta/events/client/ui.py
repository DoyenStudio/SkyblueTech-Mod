# coding=utf-8

from ..basic import ClientEvent


class UiInitFinishedEvent(ClientEvent):
    name = "UiInitFinished"

    def unmarshal(self, _):
        pass


class GridComponentSizeChangedClientEvent(ClientEvent):
    name = "GridComponentSizeChangedClientEvent"

    path = '' # type: str
    """ grid网格所在的路径（从UI根节点算起） """

    def unmarshal(self, data):
        # type: (dict) -> None
        self.path = data["path"]

    def marshal(self):
        # type: () -> dict
        return {
            "path": self.path,
        }
