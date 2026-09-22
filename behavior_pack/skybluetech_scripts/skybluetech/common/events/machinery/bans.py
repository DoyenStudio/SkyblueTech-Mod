# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class MachineBanListRequest(CustomC2SEvent):
    name = "st:MachineBanListRequest"

    def __init__(self, player_id=""):
        # type: (str) -> None
        self.player_id = player_id

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["__id__"])


class MachineBanListUpdate(CustomS2CEvent):
    name = "st:MachineBanListUpdate"

    def __init__(self, machine_ids):
        # type: (list[str]) -> None
        self.machine_ids = machine_ids

    def marshal(self):
        return {"machine_ids": self.machine_ids}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["machine_ids"])
