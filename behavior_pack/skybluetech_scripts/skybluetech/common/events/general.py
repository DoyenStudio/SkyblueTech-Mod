# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import ClientEvent, ServerEvent
from skybluetech_scripts.skybluetech.common import MOD_VERSION


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

    def __init__(self, mod_version=MOD_VERSION):
        self.MOD_VERSION = mod_version

    def marshal(self):
        return {"MOD_VERSION": self.MOD_VERSION}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["MOD_VERSION"])


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

    def __init__(self, mod_version=MOD_VERSION):
        self.MOD_VERSION = mod_version

    def marshal(self):
        return {"MOD_VERSION": self.MOD_VERSION}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["MOD_VERSION"])
