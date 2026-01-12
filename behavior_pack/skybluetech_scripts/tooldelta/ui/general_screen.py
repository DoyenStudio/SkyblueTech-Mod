# coding=utf-8
import mod.client.extraClientApi as clientApi
from ..events import ClientEvent, clientapi as event_client
from ..internal import GetModName
from .elem_comp import UBaseCtrl
from .utils import SNode, Binder

if 0:
    from typing import Callable, TypeVar
    from mod.client.ui.screenNode import ScreenNode as _ScreenNode
    from mod.client.ui.CustomUIControlProxy import CustomUIControlProxy as _CustomUIControlProxy
    T = TypeVar("T")
    CallT = TypeVar("CallT", bound=Callable)


ScreenNode = clientApi.GetScreenNodeCls()
ScreenProxy = clientApi.GetUIScreenProxyCls()


class ToolDeltaScreen(object):
    _screen_cls = None # type: type[_ScreenNode] | None
    _screen_proxy_cls = None # type: type[_CustomUIControlProxy] | None
    _screen_key = "" # type: str

    def __init__(self, screen_name, screen_instance):
        # type: (str, _ScreenNode | _CustomUIControlProxy) -> None
        self._screen_name = screen_name
        self._screen_instance = screen_instance
        self._screen_node = self.base = screen_instance if isinstance(screen_instance, ScreenNode) else screen_instance.screenNode # type: _ScreenNode # type: ignore
        self._activated = False
        self._element_cacher = {} # type: dict[str, UBaseCtrl]
        self._vars = {}
        self._ui_bound_events = [] # type: list[tuple[type[ClientEvent], Callable[[ClientEvent], None], int]]
        self._analyze_reflections()

    def AddElement(self, ctrl_def_name, ctrl_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        return UBaseCtrl(
            self, 
            self.base.CreateChildControl(ctrl_def_name, ctrl_name, None, force_update) # type: ignore
        )

    def GetElement(self, path):
        # type: (str | SNode) -> UBaseCtrl
        if isinstance(path, SNode):
            path = path.base
        return self._get_element_cache(path)

    @classmethod
    def CreateUI(cls, params={}):
        if cls._screen_cls is None:
            raise Exception("CreateUI failed: screen %s not registered as ScreenNode")
        s_instance = clientApi.CreateUI(GetModName(), cls._screen_key, params)
        if not isinstance(s_instance, cls._screen_cls):
            raise Exception("CreateUI failed: return {} is not {}".format(s_instance, cls))
        return cls(s_instance.name, s_instance) # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def PushUI(cls, params={}):
        if cls._screen_cls is None:
            raise Exception("CreateUI failed: screen %s not registered as ScreenNode")
        s_instance = clientApi.PushScreen(GetModName(), cls._screen_key, params)
        if not isinstance(s_instance, cls._screen_cls):
            raise Exception("CreateUI failed: return {} is not {}".format(s_instance, cls))
        return cls(s_instance.name, s_instance) # pyright: ignore[reportAttributeAccessIssue]

    def RemoveUI(self):
        self._do_deactive()
        if isinstance(self.base, ScreenNode):
            self.base.SetRemove()
        else:
            if clientApi.GetTopUINode() is self.base:
                clientApi.PopTopUI()

    @classmethod
    def Listen(
        cls,
        event, # type: type[ClientEvent]
        priority=0
    ):
        """
        类似一般的监听装饰器, 绑定客户端监听回调函数到 Screen 上。

        随着 Screen 的创建被创建, Screen 被销毁同时监听亦被销毁。

        Args:
            event (type[ClientEvent]): 事件类
        """
        def wrapper(func):
            # type: (CallT) -> CallT
            func._tdscreen_event_listen = event
            func._tdscreen_event_listen_priority = priority
            return func
        return wrapper

    @classmethod
    def _register_as_screen(
        cls,
        screen_name, # type: str
        screen_key=None # type: str | None
    ):
        cls._screen_key = screen_key or screen_name
        def __init__(self, namespace, name, param=None):
            ScreenNode.__init__(self, namespace, name, param) # type: ignore
            self._super_screen_ins = cls(name, self)
        def OnCreate(self):
            self._super_screen_ins._on_create()
        def OnDestroy(self):
            self._super_screen_ins._on_destroy()
        def OnTicking(self):
            self._super_screen_ins._on_tick()
        attrs = {
            "__init__": __init__,
            "OnCreate": OnCreate,
            "OnDestroy": OnDestroy,
            "OnTicking": OnTicking,
        }
        attrs.update(cls._get_tdscreen_bindings())
        t = type(cls.__name__ + "_Base", (ScreenNode,), {})
        cls._screen_cls = t
        return t

    @classmethod
    def _register_as_proxy(
        cls,
        screen_name, # type: str
        screen_key=None # type: str | None
    ):
        cls._screen_key = screen_key or screen_name

        def __init__(self, screenName, screenNode):
            ScreenProxy.__init__(self, screenName, screenNode)
            self._super_screen_ins = cls(
                screenName,
                screenNode,
            )
            self.screenNode = screenNode
        def OnCreate(self):
            self._super_screen_ins._on_create()
        def OnDestroy(self):
            self._super_screen_ins._on_destroy()
        def OnTicking(self):
            self._super_screen_ins._on_tick()

        attrs = {
            "__init__": __init__,
            "OnCreate": OnCreate,
            "OnDestroy": OnDestroy,
            "OnTicking": OnTicking,
        }
        attrs.update(cls._get_tdscreen_bindings())
        t = type(cls.__name__ + "_Base", (ScreenProxy,), attrs)
        cls._screen_proxy_cls = t
        return t

    def _analyze_reflections(self):
        for key in dir(self):
            func = getattr(self, key)
            if hasattr(func, '_tdscreen_event_listen'):
                event = func._tdscreen_event_listen
                priority = func._tdscreen_event_listen_priority
                self._ui_bound_events.append((event, func, priority))

    @classmethod
    def _get_tdscreen_bindings(cls):
        attrs = {} # type: dict[str, Callable]
        for key in dir(cls):
            func = getattr(cls, key)
            if hasattr(func, 'collection_name'):
                def wrap(_func):
                    def _wrapper(self, *args):
                        return _func(self._super_screen_ins, *args)
                    return _wrapper
                custom_binding_collections_func = wrap(func)
                custom_binding_collections_func.__module__ = func.__module__
                new_name = custom_binding_collections_func.__name__ = key + "_bindwrapper"
                attrs[new_name] = Binder.binding_collection(
                    func.binding_flags,
                    func.collection_name,
                    func.binding_name
                )(custom_binding_collections_func)
            elif hasattr(func, 'binding_flags'):
                def wrap(_func):
                    def _wrapper(self, *args):
                        return _func(self._super_screen_ins, *args)
                    return _wrapper
                custom_binding_func = wrap(func)
                custom_binding_func.__module__ = func.__module__
                new_name = custom_binding_func.__name__ = key
                attrs[new_name] = Binder.binding(
                    func.binding_flags,
                    func.binding_name
                )(custom_binding_func)
        return attrs

    def _do_active(self):
        from .pool import _addActiveToolDeltaScreen
        if self._activated:
            return
        _addActiveToolDeltaScreen(self)
        self._activated = True
        self._enable_ui_bound_listeners()

    def _do_deactive(self):
        from .pool import _removeActiveToolDeltaScreen
        if not self._activated:
            return
        _removeActiveToolDeltaScreen(self)
        self._activated = False
        self._disable_ui_bound_listeners()

    def _enable_ui_bound_listeners(self):
        for event, event_cb, priority in self._ui_bound_events:
            if issubclass(event, ClientEvent):
                event_client.AddEventListener(event, event_cb, priority)
            else:
                raise ValueError("[Error] TDScreenListen: Unsupported event type: " + event.__name__)

    def _disable_ui_bound_listeners(self):
        for event, event_cb, priority in self._ui_bound_events:
            if issubclass(event, ClientEvent):
                event_client.RemoveEventListener(event, event_cb, priority)

    def _on_create(self):
        self._do_active()
        self.OnCreate()

    def _on_destroy(self):
        self._do_deactive()
        self.OnDestroy()

    def _on_tick(self):
        self.OnTick()

    __getitem__ = GetElement

    def _get_element_cache(self, path):
        # type: (str) -> UBaseCtrl
        if path in self._element_cacher:
            return self._element_cacher[path]
        else:
            ui = UBaseCtrl(self, self.base.GetBaseUIControl(path))
            self._element_cacher[path] = ui
            return ui

    def OnCreate(self):
        "子类覆写该方法"
        pass

    def OnDestroy(self):
        "子类覆写该方法"
        pass

    def OnTick(self):
        "子类覆写该方法"
        pass

    def OnCurrentPageKeyEvent(self, event):
        pass
