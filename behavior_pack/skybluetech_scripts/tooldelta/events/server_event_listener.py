# coding=utf-8
#
import mod.server.extraServerApi as serverApi
from ..general import ServerInitCallback, ServerUninitCallback

from ..internal import GetServer, GetModName, GetModClientEngineName
from .basic import ServerEvent, CustomC2SEvent

# TYPE_CHECKING
if 0:
    from typing import Any, Callable, TypeVar
    EventT = TypeVar('EventT', bound="ServerEvent")
# TYPE_CHECKING END


listeners = {}  # type: dict[str, dict[type[ServerEvent], tuple[Callable[[Any], None], int]]]


def AddEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    """
    监听服务端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    def custom_listener(data):
        evt = event.unmarshal(data)
        listener(evt)

    funcname = listener.__module__ + "." + listener.__name__ # to avoid name conflict
    custom_listener.__name__ = funcname
    listeners.setdefault(funcname, {})[event] = (custom_listener, priority)

def RemoveEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    """
    取消监听服务端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    funcname = listener.__module__ + "." + listener.__name__
    cbs = listeners.get(funcname)
    if cbs is not None:
        fun_and_priority = cbs.pop(event, None)
        if fun_and_priority is not None:
            GetServer().UnListenForEvent(
                serverApi.GetEngineNamespace(),
                serverApi.GetEngineSystemName(),
                event.name, GetServer(),
                fun_and_priority[0], # pyright: ignore[reportArgumentType]
                priority
            )
        if not cbs:
            listeners.pop(funcname, None)

def ListenEvent(event, priority=0):
    # type: (type[EventT], int) -> Callable[[Callable[[EventT], None]], Callable[[EventT], None]]
    """
    监听服务端事件, 作为装饰器使用。

    Args:
        event (type[Event]): 事件类
    """
    def wrapper(func):
        # type: (Callable[[EventT], None]) -> Callable[[EventT], None]
        AddEventListener(event, func, priority)
        return func

    return wrapper

@ServerInitCallback(-10000)
def OnServerListen():
    # type: () -> None
    """
    需要在 server class 的 ListenEvent 方法下调用 onServerListen()
    """
    server = GetServer()
    for cb_name, event_cbs in listeners.items():
        for event, (listener, priority) in event_cbs.items():
            setattr(server, cb_name, listener)
            if issubclass(event, CustomC2SEvent):
                server.ListenForEvent(
                    GetModName(),
                    GetModClientEngineName(),
                    event.name, server,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )
            else:
                server.ListenForEvent(
                    serverApi.GetEngineNamespace(),
                    serverApi.GetEngineSystemName(),
                    event.name, server,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )

@ServerUninitCallback(-10000)
def OnServerUnlisten():
    # type: () -> None
    """
    需要在 server class 的 ListenEvent 方法下调用 onServerUnlisten()
    """
    server = GetServer()
    for _, event_cbs in listeners.items():
        for event, (listener, priority) in event_cbs.items():
            if issubclass(event, CustomC2SEvent):
                server.UnListenForEvent(
                    GetModName(),
                    GetModClientEngineName(),
                    event.name, server,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )
            else:
                server.UnListenForEvent(
                    serverApi.GetEngineNamespace(),
                    serverApi.GetEngineSystemName(),
                    event.name, server,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )
