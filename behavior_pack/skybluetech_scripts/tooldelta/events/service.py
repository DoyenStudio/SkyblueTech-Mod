# coding=utf-8
from collections import deque
from .basic import ClientEvent, ServerEvent


if 0:
    from typing import Callable, TypeVar

    CEventT = TypeVar("CEventT", bound=ClientEvent)
    SEventT = TypeVar("SEventT", bound=ServerEvent)
    CallT = TypeVar("CallT", bound=Callable)

_ATTR_EVENT_LISTENER = "_tdbind_event_listen"


class ClientListenerService:
    def __init__(self):
        self._bind_listen_events = []  # type: list[tuple[type[ClientEvent], Callable[[ClientEvent], None], int]]
        self._bind_delayed_listen_events = {}  # type: dict[type[ClientEvent], list[Callable[[ClientEvent], None]]]
        self._delayed_events_deque = deque()  # type: deque[ClientEvent]
        self._listen_service_enabled = False
        self._process_bind_listeners()
        self._enable_delayed_listeners()

    @classmethod
    def Listen(
        cls,
        event,  # type: type[CEventT]
        priority=0,
    ):

        def wrapper(func):
            # type: (CallT) -> CallT
            former = getattr(func, _ATTR_EVENT_LISTENER, [])
            former.append((event, priority))
            setattr(func, _ATTR_EVENT_LISTENER, former)
            return func

        return wrapper

    def enable_listeners(self):
        from .client_event_listener import dynListen as cDynListen

        self._listen_service_enabled = True
        self._process_all_delayed_events()
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ClientEvent):
                cDynListen(event, event_cb, priority)

    def disable_listeners(self):
        from .client_event_listener import dynUnListen as cDynUnListen

        self._listen_service_enabled = False
        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ClientEvent):
                cDynUnListen(event, event_cb, priority)

    def _enable_delayed_listeners(self):
        from .client_event_listener import dynListen as cDynListen

        for event in self._bind_delayed_listen_events:
            if issubclass(event, ClientEvent):
                cDynListen(event, self._process_delayed_event)

    def _disable_delayed_listeners(self):
        from .client_event_listener import dynUnListen as cDynUnListen

        for event in self._bind_delayed_listen_events:
            if issubclass(event, ClientEvent):
                cDynUnListen(event, self._process_delayed_event)

    def _process_delayed_event(self, event):
        # type: (ClientEvent) -> None
        if self._listen_service_enabled:
            for cb in self._bind_delayed_listen_events.get(event.__class__, []):
                cb(event)
        else:
            self._delayed_events_deque.append(event)

    def _process_all_delayed_events(self):
        while self._delayed_events_deque:
            event = self._delayed_events_deque.popleft()
            self._process_delayed_event(event)

    def _process_bind_listeners(self):
        for key in dir(self):
            attr = getattr(self, key)
            if hasattr(attr, _ATTR_EVENT_LISTENER):
                events = getattr(attr, _ATTR_EVENT_LISTENER)
                for event, priority in events:
                    self._bind_listen_events.append((event, attr, priority))

    def __del__(self):
        self._disable_delayed_listeners()


class ServerListenerService:
    def __init__(self):
        self._bind_listen_events = []  # type: list[tuple[type[ServerEvent], Callable[[ServerEvent], None], int]]
        self._process_bind_listeners()

    def enable_listeners(self):
        from .server_event_listener import dynListen as sDynListen

        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ServerEvent):
                sDynListen(event, event_cb, priority)

    def disable_listeners(self):
        from .server_event_listener import dynUnListen as sDynUnListen

        for event, event_cb, priority in self._bind_listen_events:
            if issubclass(event, ServerEvent):
                sDynUnListen(event, event_cb, priority)

    def _process_bind_listeners(self):
        for key in dir(self):
            attr = getattr(self, key)
            if hasattr(attr, _ATTR_EVENT_LISTENER):
                events = getattr(attr, _ATTR_EVENT_LISTENER)
                for event, priority in events:
                    self._bind_listen_events.append((event, attr, priority))

    @classmethod
    def Listen(
        cls,
        event,  # type: type[SEventT]
        priority=0,
    ):

        def wrapper(func):
            # type: (CallT) -> CallT
            former = getattr(func, _ATTR_EVENT_LISTENER, [])
            former.append((event, priority))
            setattr(func, _ATTR_EVENT_LISTENER, former)
            return func

        return wrapper
