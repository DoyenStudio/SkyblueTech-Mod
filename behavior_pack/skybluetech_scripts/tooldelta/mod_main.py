# coding=utf-8
#
from mod.common.mod import Mod
from mod_log import logger
from .internal import (
    SetModName,
    GetModName,
    GetModServerEngineName,
    GetModClientEngineName,
)


def RegisterMod():
    def wrapper(cls):
        # type: (type[ToolDeltaMod]) -> type[ToolDeltaMod]
        if cls.name is None:
            raise ValueError("mod name is None")
        SetModName(cls.name)
        return Mod.Binding(name=cls.name, version=cls.version_str())(cls)  # pyright: ignore[reportOptionalCall]

    return wrapper


class ToolDeltaMod(object):
    name = None  # type: str | None
    version = (1, 0, 0)  # type: tuple[int, int, int]

    def __init__(self):
        pass

    def OnServerInited(self):
        pass

    def OnClientInited(self):
        pass

    @Mod.InitServer()  # pyright: ignore[reportOptionalCall]
    def _init_mod_server(self):
        import mod.server.extraServerApi as serverApi
        from .mod_server import ToolDeltaModServer

        server_system_name = GetModServerEngineName()
        server_system_path = (
            ToolDeltaModServer.__module__ + "." + ToolDeltaModServer.__name__
        )
        self.OnServerInited()
        serverApi.RegisterSystem(GetModName(), server_system_name, server_system_path)
        logger.debug("ToolDelta: Mod server inited: " + server_system_name)

    @Mod.InitClient()  # pyright: ignore[reportOptionalCall]
    def _init_mod_client(self):
        import mod.client.extraClientApi as clientApi
        from .mod_client import ToolDeltaModClient

        client_system_name = GetModClientEngineName()
        client_system_path = (
            ToolDeltaModClient.__module__ + "." + ToolDeltaModClient.__name__
        )
        self.OnClientInited()
        clientApi.RegisterSystem(GetModName(), client_system_name, client_system_path)
        logger.debug("ToolDelta: Mod client inited: " + client_system_name)

    @classmethod
    def version_str(cls):
        return ".".join(map(str, cls.version))
