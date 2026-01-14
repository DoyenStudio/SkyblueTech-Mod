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

event_listeners = {}  # type: dict[int, dict[type[ClientEvent], list[tuple[int, Callable[[Any], None]]]]]
system_event_listeners = {} # type: dict[int, dict[type[ClientEvent], Callable[[dict], None]]]
system_inited = False


def AddEventListener(event, listener, priority=0, inner_priority=0):
    # type: (type[EventT], Callable[[EventT], None], int, int) -> None
    """
    监听客户端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    dynListen(event, listener, priority, inner_priority)
    

def RemoveEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    """
    取消监听服务端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    dynUnListen(event, listener, priority)

def ListenEvent(event, priority=0, inner_priority=0):
    # type: (type[EventT], int, int) -> Callable[[Callable[[EventT], None]], Callable[[EventT], None]]
    """
    监听客户端事件, 作为装饰器使用。

    Args:
        event (type[Event]): 事件类
    """
    def wrapper(func):
        # type: (Callable[[EventT], None]) -> Callable[[EventT], None]
        AddEventListener(event, func, priority, inner_priority)
        return func

    return wrapper

def dynListen(event, listener, priority=0, inner_priority=0):
    # type: (type[EventT], Callable[[EventT], None], int, int) -> None
    global system_inited
    if priority not in event_listeners or event not in event_listeners[priority]:
        def event_bus_handler(args):
            # type: (dict) -> None
            event_ins = event.unmarshal(args)
            for _, cb in event_listeners[priority][event]:
                cb(event_ins)
        event_bus_handler.__name__ = "tdsysevent_handler_" + event.__name__ + str(priority)
        system_event_listeners.setdefault(priority, {})[event] = event_bus_handler
        if system_inited:
            addSysEventListener(event, event_bus_handler, priority)
    event_listeners.setdefault(priority, {}).setdefault(event, []).append((inner_priority, listener))
    event_listeners[priority][event].sort(key=lambda x: x[0], reverse=True)
        
def dynUnListen(event, listener, priority=0, inner_priority=0):
    # type: (type[EventT], Callable[[EventT], None], int, int) -> None
    global system_inited
    if priority not in event_listeners or event not in event_listeners[priority]:
        print("[Warning] Remove listener not exists: {}".format(listener))
        return
    event_listeners[priority][event].remove((inner_priority, listener))
    if not event_listeners[priority][event]:
        del event_listeners[priority][event]
        syslevel_listeners = system_event_listeners[priority]
        syslevel_listener = syslevel_listeners.pop(event)
        if system_inited:
            remSysEventListener(event, syslevel_listener, priority)
        if not syslevel_listeners:
            del system_event_listeners[priority]

def addSysEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[dict], None], int) -> None
    s = GetClient()
    setattr(s, listener.__name__, listener)
    if issubclass(event, CustomS2CEvent):
        namespace = GetModName()
        system_name = GetModServerEngineName()
    else:
        namespace = clientApi.GetEngineNamespace()
        system_name = clientApi.GetEngineSystemName()
    s.ListenForEvent(
        namespace,
        system_name,
        event.name, s,
        listener, # pyright: ignore[reportArgumentType]
        priority
    )

def remSysEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[dict], None], int) -> None
    s = GetClient()
    if hasattr(s, listener.__name__):
        delattr(s, listener.__name__)
    if issubclass(event, CustomS2CEvent):
        namespace = GetModName()
        system_name = GetModServerEngineName()
    else:
        namespace = clientApi.GetEngineNamespace()
        system_name = clientApi.GetEngineSystemName()
    s.UnListenForEvent(
        namespace,
        system_name,
        event.name, s,
        listener, # pyright: ignore[reportArgumentType]
        priority
    )

@ClientInitCallback(-10000)
def onClientListen():
    # type: () -> None
    global system_inited
    for priority, syslevel_cbs in system_event_listeners.items():
        for event, listener in syslevel_cbs.items():
            addSysEventListener(event, listener, priority)
    system_inited = True

@ClientUninitCallback(-10000)
def onClientUnlisten():
    # type: () -> None
    for priority, syslevel_cbs in system_event_listeners.items():
        for event, listener in syslevel_cbs.items():
            remSysEventListener(event, listener, priority)

