# coding=utf-8
"""管线客户端识别快照；仅同步类别和方块 ID，不同步服务端回调。"""
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class TransmitterRegistryRequest(CustomC2SEvent):
    name = "st:TmRegistryRequest"

    def __init__(self, player_id=""):
        self.player_id = player_id

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["__id__"])


class TransmitterRegistrySnapshot(CustomS2CEvent):
    name = "st:TmRegistrySnapshot"

    def __init__(self, kinds):
        self.kinds = kinds

    def marshal(self):
        return {"kinds": self.kinds}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["kinds"])
