# coding=utf-8
#
import mod.server.extraServerApi as serverApi
from ..general import ServerInitCallback, ServerUninitCallback

from ..internal import GetServer, GetModName, GetModClientEngineName
from .basic import ServerEvent, CustomC2SEvent

# TYPE_CHECKING
if 0:
    from typing import Any, Callable, TypeVar

    EventT = TypeVar("EventT", bound="ServerEvent")
# TYPE_CHECKING END


event_listeners = {}  # type: dict[int, dict[type[ServerEvent], list[Callable[[Any], None]]]]
system_event_listeners = {}  # type: dict[int, dict[type[ServerEvent], Callable[[dict], None]]]
system_inited = False


def AddEventListener(event, listener, priority=0, static=False):
    # type: (type[EventT], Callable[[EventT], None], int, bool) -> None
    """
    监听服务端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
        priority (int): 优先级
        static (bool): 是否静态监听, 即不被热重载影响
    """
    global system_inited
    if system_inited and static:
        return
    dynListen(event, listener, priority)


def RemoveEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    """
    取消监听服务端事件。

    Args:
        event (type[Event]): 事件类
        listener ((T) -> None): 事件监听器
    """
    dynUnListen(event, listener, priority)


def ListenEvent(event, priority=0, static=False):
    # type: (type[EventT], int, bool) -> Callable[[Callable[[EventT], None]], Callable[[EventT], None]]
    """
    监听服务端事件, 作为装饰器使用。

    Args:
        event (type[Event]): 事件类
    """

    def wrapper(func):
        # type: (Callable[[EventT], None]) -> Callable[[EventT], None]
        AddEventListener(event, func, priority, static)
        return func

    return wrapper


def dynListen(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    global system_inited
    if priority not in event_listeners or event not in event_listeners[priority]:

        def event_bus_handler(args):
            # type: (dict) -> None
            event_ins = event.unmarshal(args)
            for cb in event_listeners[priority][event]:
                cb(event_ins)

        event_bus_handler.__name__ = (
            "tdsysevent_handler_" + event.__name__ + str(priority)
        )
        system_event_listeners.setdefault(priority, {})[event] = event_bus_handler
        if system_inited:
            addSysEventListener(event, event_bus_handler, priority)
    listeners = event_listeners.setdefault(priority, {}).setdefault(event, [])
    if listener not in listeners:
        # to avoid hot reload duplicated
        listeners.append(listener)


def dynUnListen(event, listener, priority=0):
    # type: (type[EventT], Callable[[EventT], None], int) -> None
    global system_inited
    if priority not in event_listeners or event not in event_listeners[priority]:
        print("[Warning] Remove listener not exists: {}".format(listener))
        return
    event_listeners[priority][event].remove(listener)
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
    s = GetServer()
    setattr(s, listener.__name__, listener)
    if issubclass(event, CustomC2SEvent):
        namespace = GetModName()
        system_name = GetModClientEngineName()
    else:
        namespace = serverApi.GetEngineNamespace()
        system_name = serverApi.GetEngineSystemName()
    s.ListenForEvent(
        namespace,
        system_name,
        event.name,
        s,
        listener,  # pyright: ignore[reportArgumentType]
        priority,
    )


def remSysEventListener(event, listener, priority=0):
    # type: (type[EventT], Callable[[dict], None], int) -> None
    s = GetServer()
    if hasattr(s, listener.__name__):
        delattr(s, listener.__name__)
    if issubclass(event, CustomC2SEvent):
        namespace = GetModName()
        system_name = GetModClientEngineName()
    else:
        namespace = serverApi.GetEngineNamespace()
        system_name = serverApi.GetEngineSystemName()
    s.UnListenForEvent(
        namespace,
        system_name,
        event.name,
        s,
        listener,  # pyright: ignore[reportArgumentType]
        priority,
    )


@ServerInitCallback(-10000)
def onServerListen():
    # type: () -> None
    global system_inited
    for priority, syslevel_cbs in system_event_listeners.items():
        for event, listener in syslevel_cbs.items():
            addSysEventListener(event, listener, priority)
    system_inited = True


@ServerUninitCallback(-10000)
def onServerUnlisten():
    # type: () -> None
    for priority, syslevel_cbs in system_event_listeners.items():
        for event, listener in syslevel_cbs.items():
            remSysEventListener(event, listener, priority)
