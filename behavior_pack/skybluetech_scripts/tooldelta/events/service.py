# coding=utf-8
from .basic import ClientEvent, ServerEvent
from .client_event_listener import dynListen as cDynListen
from .server_event_listener import dynListen as sDynListen

if 0:
    from typing import Callable, TypeVar

    CEventT = TypeVar("CEventT", bound=ClientEvent)
    SEventT = TypeVar("SEventT", bound=ServerEvent)
    CallT = TypeVar("CallT", bound=Callable)

_ATTR_EVENT_LISTENER = "_tdbind_event_listen"
_ATTR_EVENT_LISTENER_PRIORITY = "_tdbind_event_listen_priority"


class ClientListenerService:
    def __init__(self):
        self._bind_listen_events = []  # type: list[tuple[type[ClientEvent], Callable[[ClientEvent], None], int]]
        self._process_bind_listeners()

    def enable_listeners(self):
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ClientEvent):
                cDynListen(event, event_cb, priority)
            else:
                raise ValueError(
                    "[Error] TDScreenListen: Unsupported event type: " + event.__name__
                )

    def disable_listeners(self):
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ClientEvent):
                cDynListen(event, event_cb, priority)

    def _process_bind_listeners(self):
        for key in dir(self):
            attr = getattr(self, key)
            if hasattr(attr, _ATTR_EVENT_LISTENER):
                event = getattr(attr, _ATTR_EVENT_LISTENER)
                priority = getattr(attr, _ATTR_EVENT_LISTENER_PRIORITY)
                self._bind_listen_events.append((event, attr, priority))

    @classmethod
    def Listen(
        cls,
        event,  # type: type[CEventT]
        priority=0,
    ):

        def wrapper(func):
            # type: (CallT) -> CallT
            setattr(func, _ATTR_EVENT_LISTENER, event)
            setattr(func, _ATTR_EVENT_LISTENER_PRIORITY, priority)
            return func

        return wrapper


class ServerListenerService:
    def __init__(self):
        self._bind_listen_events = []  # type: list[tuple[type[ServerEvent], Callable[[ServerEvent], None], int]]
        self._process_bind_listeners()

    def enable_listeners(self):
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ServerEvent):
                sDynListen(event, event_cb, priority)
            else:
                raise ValueError(
                    "[Error] TDScreenListen: Unsupported event type: " + event.__name__
                )

    def disable_listeners(self):
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ServerEvent):
                sDynListen(event, event_cb, priority)

    def _process_bind_listeners(self):
        for key in dir(self):
            attr = getattr(self, key)
            if hasattr(attr, _ATTR_EVENT_LISTENER):
                event = getattr(attr, _ATTR_EVENT_LISTENER)
                priority = getattr(attr, _ATTR_EVENT_LISTENER_PRIORITY)
                self._bind_listen_events.append((event, attr, priority))

    @classmethod
    def Listen(
        cls,
        event,  # type: type[SEventT]
        priority=0,
    ):

        def wrapper(func):
            # type: (CallT) -> CallT
            setattr(func, _ATTR_EVENT_LISTENER, event)
            setattr(func, _ATTR_EVENT_LISTENER_PRIORITY, priority)
            return func

        return wrapper
