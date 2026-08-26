# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import ClientEvent, ServerEvent


class SkyblueTechClientLoaded(ClientEvent):
    name = "SkyblueTechClientLoaded"

    def __init__(self):
        pass

    def marshal(self):
        pass

    @classmethod
    def unmarshal(cls, _):
        pass

class SkyblueTechServerLoaded(ServerEvent):
    name = "SkyblueTechServerLoaded"

    def __init__(self):
        pass

    def marshal(self):
        pass

    @classmethod
    def unmarshal(cls, _):
        pass
