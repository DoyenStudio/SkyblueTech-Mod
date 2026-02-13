from ..internal import GetServer, GetClient


class BaseEvent(object):
    name = "Event"

    @classmethod
    def unmarshal(
        cls,
        data,  # type: dict
    ):
        return cls()


class ServerEvent(BaseEvent):
    name = "ServerEvent"

    @classmethod
    def Listen(cls, priority=0):
        """
        将以下的方法修饰为监听回调。

        Args:
            priority (int, optional): 优先级, 默认为 0
        """
        _requireServerListenerModule()
        return ServerListenEvent(cls, priority, static=True)


class ClientEvent(BaseEvent):
    name = "ClientEvent"

    @classmethod
    def Listen(cls, priority=0, inner_priority=0):
        """
        将以下的方法修饰为监听回调。

        Args:
            priority (int, optional): 优先级, 默认为 0
        """
        _requireClientListenerModule()
        return ClientListenEvent(cls, priority, inner_priority, static=True)


class CustomC2SEvent(ServerEvent):
    """
    表示一个由客户端发送的、需要被服务端监听的通信事件。
    """

    name = "CustomServerEvent"

    def marshal(self):  # type: () -> dict
        raise NotImplementedError

    def send(self):
        from .notify import NotifyToServer

        NotifyToServer(self)


class CustomS2CEvent(ClientEvent):
    """
    表示一个由服务端发送的、需要被客户端监听的通信事件。
    """

    name = "CustomClientEvent"

    def marshal(self):  # type: () -> dict
        raise NotImplementedError

    def send(self, client_id):
        # type: (str) -> None
        from .notify import NotifyToClient

        NotifyToClient(client_id, self)

    def sendMulti(self, client_ids):
        # type: (list[str]) -> None
        from .notify import NotifyToClients

        NotifyToClients(client_ids, self)

    def sendAll(self):
        # type: () -> None
        from .notify import NotifyToAll

        NotifyToAll(self)


def NewClientEventData():
    return GetClient().CreateEventData()


def NewServerEventData():
    return GetServer().CreateEventData()


_serverListenerModLoaded = False
_clientListenerModLoaded = False


def _requireServerListenerModule():
    global ServerListenEvent, _serverListenerModLoaded
    if not _serverListenerModLoaded:
        from .server_event_listener import ListenEvent as ServerListenEvent

        _serverListenerModLoaded = True


def _requireClientListenerModule():
    global ClientListenEvent, _clientListenerModLoaded
    if not _clientListenerModLoaded:
        from .client_event_listener import ListenEvent as ClientListenEvent

        _clientListenerModLoaded = True
