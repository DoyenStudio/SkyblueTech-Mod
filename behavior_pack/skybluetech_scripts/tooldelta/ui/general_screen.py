# coding=utf-8
import mod.client.extraClientApi as clientApi
from ..events.service import ClientListenerService
from ..internal import GetModName
from .elem_comp import UBaseCtrl
from .utils import UIPath, Binder

if 0:
    import typing
    from ._ui_typing import ScreenNode as _ScreenNode
    from ._ui_typing import (
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
        self._vars = {}
        self._load_ctrls = set()  # type: set[UBaseCtrl]

    @classmethod
    def convertFrom(
        cls,
        screen_node,  # type: _ScreenNode
    ):
        "将原版 ScreenNode 转换为 ToolDeltaScreen"
        instance = cls(screen_node.name, screen_node)

        # not safe
        instance._do_active()

        # wrap Destroy
        _orig_on_destroy = getattr(screen_node.Destroy, "_origin_on_destroy", None)
        if _orig_on_destroy is None:
            _orig_on_destroy = screen_node.Destroy

        def _wrap_on_destroy():
            instance._on_destroy()
            _orig_on_destroy()

        screen_node.Destroy = _wrap_on_destroy
        _wrap_on_destroy._origin_on_destroy = screen_node.Destroy

        return instance

    def AddElement(self, ctrl_def_name, ctrl_name, force_update=True, _parent=None):
        # type: (str, str, bool, UBaseCtrl | None) -> UBaseCtrl
        return UBaseCtrl(
            self,
            self.base.CreateChildControl(
                ctrl_def_name,
                ctrl_name,
                _parent.base if _parent is not None else None,
                force_update,
            ),
        )

    def GetBaseUIControl(
        self,
        path,  # type: str | UIPath
    ):
        if isinstance(path, UIPath):
            path = path.base
        return self.base.GetBaseUIControl(path)

    def GetElement(self, path):
        # type: (str | UIPath) -> UBaseCtrl
        if isinstance(path, UIPath):
            path = path.base
        c = UBaseCtrl(self, self.GetBaseUIControl(path))
        self._add_sub_ctrl(c)
        return c

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
            raise Exception(
                "CreateUI failed: screen %s not registered as ScreenNode" % cls.__name__
            )
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
        screen_key,  # type: str
    ):
        cls._screen_key = screen_key

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

        def OnActive(self):
            self._super_screen_ins._on_active()

        def OnDeactive(self):
            self._super_screen_ins._on_deactive()

        attrs = {
            "__init__": __init__,
            "Create": Create,
            "Destory": Destory,
            "Update": Update,
            "OnActive": OnActive,
            "OnDeactive": OnDeactive,
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
        self._disable_delayed_listeners()
        for ctrl in list(self._load_ctrls):
            ctrl._call_destroy()
        self._load_ctrls.clear()

    def _add_sub_ctrl(self, ctrl):
        # type: (UBaseCtrl) -> None
        self._load_ctrls.add(ctrl)

    def _remove_sub_ctrl(self, ctrl, from_top_removal=False):
        # type: (UBaseCtrl, bool) -> bool
        if ctrl not in self._load_ctrls:
            return False
        self._load_ctrls.remove(ctrl)
        if from_top_removal:
            return self.base.RemoveChildControl(ctrl.base)
        else:
            return True

    def _on_create(self):
        self._do_active()
        self.OnCreate()

    def _on_destroy(self):
        self._do_deactive()
        self.OnDestroy()

    def _on_active(self):
        self.OnActive()

    def _on_deactive(self):
        self.OnDeactive()

    def _on_ticking(self):
        self.OnTicking()

    __getitem__ = GetElement

    def OnCreate(self):
        "子类覆写该方法"
        pass

    def OnDestroy(self):
        "子类覆写该方法"
        pass

    def OnActive(self):
        "子类覆写该方法"
        pass

    def OnDeactive(self):
        "子类覆写该方法"
        pass

    def OnTicking(self):
        "子类覆写该方法"
        pass
