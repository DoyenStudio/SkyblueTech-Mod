# coding=utf-8
import mod.client.extraClientApi as clientApi
from ..events.service import ClientListenerService
from ..internal import GetModName
from .elem_comp import UBaseCtrl
from .utils import UIPath, Binder

if 0:
    from mod.client.ui.screenNode import ScreenNode as _ScreenNode
    from mod.client.ui.CustomUIScreenProxy import (
        CustomUIScreenProxy as _CustomUIControlProxy,
    )


ScreenNode = clientApi.GetScreenNodeCls()
ScreenProxy = clientApi.GetUIScreenProxyCls()


class ToolDeltaScreen(ClientListenerService):
    _ATTR_EVENT_LISTENER = "_tdscreen_event_listen"
    _ATTR_EVENT_LISTENER_PRIORITY = "_tdscreen_event_listen_priority"

    _screen_cls = None  # type: type[_ScreenNode] | None
    _screen_proxy_cls = None  # type: type[_CustomUIControlProxy] | None
    _screen_key = ""  # type: str

    def __init__(self, screen_name, screen_instance, params=None):
        # type: (str, _ScreenNode | _CustomUIControlProxy, dict | None) -> None
        ClientListenerService.__init__(self)
        self._screen_name = screen_name
        self._screen_instance = screen_instance
        self._init_params = params or {}
        self._screen_node = self.base = (
            screen_instance
            if isinstance(screen_instance, ScreenNode)
            else getattr(screen_instance, "screenNode")
        )
        self._activated = False
        self._element_cacher = {}  # type: dict[str, UBaseCtrl]
        self._vars = {}

    def AddElement(self, ctrl_def_name, ctrl_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        return UBaseCtrl(
            self,
            self.base.CreateChildControl(ctrl_def_name, ctrl_name, None, force_update),  # type: ignore
        )

    def GetElement(self, path):
        # type: (str | UIPath) -> UBaseCtrl
        if isinstance(path, UIPath):
            path = path.base
        return self._get_element_cache(path)

    @classmethod
    def CreateUI(cls, params={}):
        if cls._screen_cls is None:
            raise Exception("CreateUI failed: screen %s not registered as ScreenNode")
        screen = clientApi.CreateUI(GetModName(), cls._screen_key, params)
        if not isinstance(screen, cls._screen_cls):
            raise Exception("CreateUI failed: return {} is not {}".format(screen, cls))
        self = getattr(screen, "_super_screen_ins")
        if not isinstance(self, cls):
            raise ValueError(
                "CreateUI failed: internal: return {} is not {}".format(self, cls)
            )
        return self

    @classmethod
    def PushUI(cls, params={}):
        if cls._screen_cls is None:
            raise Exception("CreateUI failed: screen %s not registered as ScreenNode")
        screen = clientApi.PushScreen(GetModName(), cls._screen_key, params)
        if not isinstance(screen, cls._screen_cls):
            raise Exception("CreateUI failed: return {} is not {}".format(screen, cls))
        self = getattr(screen, "_super_screen_ins")
        if not isinstance(self, cls):
            raise ValueError(
                "CreateUI failed: internal: return {} is not {}".format(self, cls)
            )
        return self

    def RemoveUI(self):
        self._do_deactive()
        if isinstance(self.base, ScreenNode):
            self.base.SetRemove()
        else:
            if clientApi.GetTopUINode() is self.base:
                clientApi.PopTopUI()

    @classmethod
    def _register_as_screen(
        cls,
        screen_name,  # type: str
        screen_key=None,  # type: str | None
    ):
        cls._screen_key = screen_key or screen_name

        def __init__(self, namespace, name, param=None):
            ScreenNode.__init__(self, namespace, name, param)  # type: ignore
            self._initial_params = param
            self._super_screen_ins = cls(name, self, param)

        def Create(self):
            self._super_screen_ins._on_create()

        def Destory(self):
            self._super_screen_ins._on_destroy()

        def Update(self):
            self._super_screen_ins._on_ticking()

        attrs = {
            "__init__": __init__,
            "Create": Create,
            "Destory": Destory,
            "Update": Update,
        }
        attrs.update(cls._get_tdscreen_bindings())
        t = type(cls.__name__ + "_Base", (ScreenNode,), attrs)
        cls._screen_cls = t
        return t

    @classmethod
    def _register_as_proxy(
        cls,
        screen_name,  # type: str
        screen_key=None,  # type: str | None
    ):
        cls._screen_key = screen_key or screen_name

        def __init__(self, screenName, screenNode):
            ScreenProxy.__init__(self, screenName, screenNode)
            self._initial_params = None
            self.screenNode = screenNode
            self._super_screen_ins = cls(
                screenName,
                screenNode,
            )

        def OnCreate(self):
            self._super_screen_ins._on_create()

        def OnDestroy(self):
            self._super_screen_ins._on_destroy()

        def OnTick(self):
            self._super_screen_ins._on_ticking()

        attrs = {
            "__init__": __init__,
            "OnCreate": OnCreate,
            "OnDestroy": OnDestroy,
            "OnTick": OnTick,
        }
        attrs.update(cls._get_tdscreen_bindings())
        t = type(cls.__name__ + "_Base", (ScreenProxy,), attrs)
        cls._screen_proxy_cls = t
        return t

    @classmethod
    def _get_tdscreen_bindings(cls):
        attrs = {}
        for key in dir(cls):
            attr = getattr(cls, key)
            if hasattr(attr, "collection_name"):

                def wrap(_func):
                    def _wrapper(self, *args):
                        return _func(self._super_screen_ins, *args)

                    return _wrapper

                custom_binding_collections_func = wrap(attr)
                custom_binding_collections_func.__module__ = attr.__module__
                new_name = custom_binding_collections_func.__name__ = (
                    key + "_bindwrapper"
                )
                attrs[new_name] = Binder.binding_collection(
                    attr.binding_flags, attr.collection_name, attr.binding_name
                )(custom_binding_collections_func)
            elif hasattr(attr, "binding_flags"):

                def wrap(_func):
                    def _wrapper(self, *args):
                        return _func(self._super_screen_ins, *args)

                    return _wrapper

                custom_binding_func = wrap(attr)
                custom_binding_func.__module__ = attr.__module__
                new_name = custom_binding_func.__name__ = key
                attrs[new_name] = Binder.binding(attr.binding_flags, attr.binding_name)(
                    custom_binding_func
                )
        return attrs

    def _do_active(self):
        from .pool import _addActiveToolDeltaScreen

        if self._activated:
            return
        _addActiveToolDeltaScreen(self)
        self._activated = True
        self.enable_listeners()

    def _do_deactive(self):
        from .pool import _removeActiveToolDeltaScreen

        if not self._activated:
            return
        _removeActiveToolDeltaScreen(self)
        self._activated = False
        self.disable_listeners()

    def _on_create(self):
        self._do_active()
        self.OnCreate()

    def _on_destroy(self):
        self._do_deactive()
        self.OnDestroy()

    def _on_ticking(self):
        self.OnTicking()

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

    def OnTicking(self):
        "子类覆写该方法"
        pass
