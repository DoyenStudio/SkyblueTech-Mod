# coding=utf-8
#
import mod.client.extraClientApi as clientApi
from ..general import ClientInitCallback, ClientUninitCallback

from ..internal import GetModName, GetModServerEngineName

# TYPE_CHECKING
if 0:
    from typing import Any, TYPE_CHECKING, Callable, TypeVar
    EventT = TypeVar("EventT", bound="ClientEvent")
    T = TypeVar("T")
# TYPE_CHECKING END

from ..internal import GetClient
from .basic import ClientEvent, CustomS2CEvent

listeners = {}  # type: dict[str, dict[type[ClientEvent], tuple[Callable[[Any], None], int]]]
system_inited = False


def AddEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    """
    监听客户端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    global system_inited
    if system_inited:
        def _custom_listener(data):
            evt = event.unmarshal(data)
            listener(evt)

        funcname = listener.__module__ + "." + listener.__name__ # to avoid name conflict
        _custom_listener.__name__ = funcname
        listeners.setdefault(funcname, {})[event] = (_custom_listener, priority) # type: ignore

        setattr(GetClient(), funcname, _custom_listener)
        if issubclass(event, CustomS2CEvent):
            GetClient().ListenForEvent(
                GetModName(),
                GetModServerEngineName(),
                event.name, GetClient(),
                _custom_listener, # pyright: ignore[reportArgumentType]
                priority
            )
        else:
            GetClient().ListenForEvent(
                clientApi.GetEngineNamespace(),
                clientApi.GetEngineSystemName(),
                event.name, GetClient(),
                _custom_listener, # pyright: ignore[reportArgumentType]
                priority,
            )
    else:
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
            GetClient().UnListenForEvent(
                clientApi.GetEngineNamespace(),
                clientApi.GetEngineSystemName(),
                event.name, GetClient(),
                fun_and_priority[0], # pyright: ignore[reportArgumentType]
                priority
            )
        if not cbs:
            listeners.pop(funcname, None)

def ListenEvent(event, priority=0):
    # type: (type[EventT], int) -> Callable[[Callable[[EventT], None]], Callable[[EventT], None]]
    """
    监听客户端事件, 作为装饰器使用。

    Args:
        event (type[Event]): 事件类
    """
    def wrapper(func):
        # type: (Callable[[EventT], None]) -> Callable[[EventT], None]
        AddEventListener(event, func, priority)
        return func

    return wrapper

@ClientInitCallback(-10000)
def OnClientListen():
    # type: () -> None
    global system_inited
    client = GetClient()
    for cb_name, event_cbs in listeners.items():
        for event, (listener, priority) in event_cbs.items():
            setattr(client, cb_name, listener)
            if issubclass(event, CustomS2CEvent):
                client.ListenForEvent(
                    GetModName(),
                    GetModServerEngineName(),
                    event.name, client, listener, # pyright: ignore[reportArgumentType]
                    priority
                )
            else:
                client.ListenForEvent(
                    clientApi.GetEngineNamespace(),
                    clientApi.GetEngineSystemName(),
                    event.name, client, listener, # pyright: ignore[reportArgumentType]
                    priority
                )
    system_inited = True

@ClientUninitCallback(-10000)
def OnClientUnlisten():
    # type: () -> None
    client = GetClient()
    for _, event_cbs in listeners.items():
        for event, (listener, priority) in event_cbs.items():
            if issubclass(event, CustomS2CEvent):
                client.UnListenForEvent(
                    GetModName(),
                    GetModServerEngineName(),
                    event.name, client,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )
            else:
                client.UnListenForEvent(
                    clientApi.GetEngineNamespace(),
                    clientApi.GetEngineSystemName(),
                    event.name, client,
                    listener, # pyright: ignore[reportArgumentType]
                    priority
                )

