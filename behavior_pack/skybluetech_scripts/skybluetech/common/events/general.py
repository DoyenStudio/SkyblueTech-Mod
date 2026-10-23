# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import ClientEvent, ServerEvent


class SkyblueTechClientLoaded(ClientEvent):
    name = "SkyblueTechClientLoaded"

    @classmethod
    def GetNamespace(cls):
        from skybluetech_scripts.tooldelta.internal import GetModName

        return GetModName()

    @classmethod
    def GetSystemName(cls):
        from skybluetech_scripts.tooldelta.internal import GetModClientEngineName

        return GetModClientEngineName()

    def __init__(self):
        pass

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, _):
        return cls()

class SkyblueTechServerLoaded(ServerEvent):
    name = "SkyblueTechServerLoaded"

    @classmethod
    def GetNamespace(cls):
        from skybluetech_scripts.tooldelta.internal import GetModName

        return GetModName()

    @classmethod
    def GetSystemName(cls):
        from skybluetech_scripts.tooldelta.internal import GetModServerEngineName

        return GetModServerEngineName()

    def __init__(self):
        pass

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, _):
        return cls()
