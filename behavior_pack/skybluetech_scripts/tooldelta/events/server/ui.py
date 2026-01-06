# coding=utf-8

from ..basic import CustomS2CEvent


class CreateUIRequest(CustomS2CEvent):
    name = "CreateUIRequest"

    def __init__(self, ui_key="", sync_id=""):
        # type: (str, str) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id

    def marshal(self):
        return {"key": self.ui_key, "sid": self.sync_id}

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["key"]
        self.sync_id = data.get("sid")


class PushUIRequest(CreateUIRequest):
    name = "PushUIRequest"


class ForceRemoveUIRequest(CustomS2CEvent):
    name = "ForceRemoveUIRequest"

    def __init__(self, ui_key=""):
        # type: (str) -> None
        self.ui_key = ui_key

    def marshal(self):
        return {"key": self.ui_key}

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["key"]
