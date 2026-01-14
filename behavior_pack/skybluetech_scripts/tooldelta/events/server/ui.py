# coding=utf-8

from ..basic import CustomS2CEvent


class CreateUIRequest(CustomS2CEvent):
    name = "CreateUIRequest"

    def __init__(self, ui_key, sync_id="", params={}):
        # type: (str, str, dict) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id
        self.params = params

    def marshal(self):
        return {"key": self.ui_key, "sid": self.sync_id, "params": self.params}

    @classmethod
    def unmarshal(cls, data):
        # self.ui_key = data["key"]
        # self.sync_id = data.get("sid")
        # self.params = data["params"].copy()
        # self.params["sync_id"] = self.sync_id
        params = data["params"].copy()
        params["sync_id"] = data.get("sid", "")
        return cls(
            ui_key=data["key"],
            sync_id=data.get("sid", ""),
            params=params,
        )


class PushUIRequest(CreateUIRequest):
    name = "PushUIRequest"


class ForceRemoveUIRequest(CustomS2CEvent):
    name = "ForceRemoveUIRequest"

    def __init__(self, ui_key=""):
        # type: (str) -> None
        self.ui_key = ui_key

    def marshal(self):
        return {"key": self.ui_key}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            ui_key=data["key"],
        )
