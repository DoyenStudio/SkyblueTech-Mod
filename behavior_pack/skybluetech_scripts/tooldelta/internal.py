# coding=utf-8

from threading import current_thread


# TYPE_CHECKING
if 0:
    from .mod_server import ToolDeltaModServer as Server
    from .mod_client import ToolDeltaModClient as Client
# TYPE_CHECKING END


class Runtime:
    server = None  # type: Server | None
    client = None  # type: Client | None
    modName = None  # type: str | None
    server_thread_ident = None  # type: int | None
    client_thread_ident = None  # type: int | None


def GetServer():
    # type: () -> Server
    if Runtime.server is None:
        raise RuntimeError("Server is not initialized")
    return Runtime.server


def SetServer(server):
    # type: (Server) -> None
    Runtime.server = server
    Runtime.server_thread_ident = current_thread().ident


def GetClient():  # type: () -> Client
    if Runtime.client is None:
        raise RuntimeError("Client is not initialized")
    return Runtime.client


def SetClient(client):
    # type: (Client) -> None
    Runtime.client = client
    Runtime.client_thread_ident = current_thread().ident


def GetModName():
    if Runtime.modName is None:
        raise RuntimeError("modName is not initialized")
    return Runtime.modName


def SetModName(mod_name):
    # type: (str) -> None
    Runtime.modName = mod_name


def GetModServerEngineName():
    return GetModName() + ".TDServer"


def GetModClientEngineName():
    return GetModName() + ".TDClient"


def inClientEnv():
    return current_thread().ident == Runtime.client_thread_ident


def inServerEnv():
    return current_thread().ident == Runtime.server_thread_ident


def InServerEnv():
    if inServerEnv():
        return True
    elif not inClientEnv():
        raise Exception("Not in client or server env")
    else:
        return False


InClientEnv = inClientEnv
