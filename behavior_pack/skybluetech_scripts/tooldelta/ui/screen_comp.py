# coding=utf-8
import uuid
import mod.client.extraClientApi as clientApi
from ..internal import GetModName
from ..events.client.control import OnKeyPressInGame
from .utils import SNode
from .elem_comp import UBaseCtrl
from .functions import addElement


ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()


class UScreenNode(ScreenNode):
    bound_ui = None # type: str | None
    _key = "???"
    top_node = None # type: SNode | None

    def __init__(self, namespace, screenName, param=None):
        ScreenNode.__init__(self, namespace, screenName, param) # type: ignore
        self.screen_name = screenName
        self.base = self
        self.activated = False
        self._elem_cacher = {} # type: dict[str, UBaseCtrl]
        self._vars = {}
        self._bind_data = {}

    @classmethod
    def CreateUI(cls, params={}):
        # params["isHud"] = int(isHud)
        n = clientApi.CreateUI(GetModName(), cls._key, params)
        if not isinstance(n, cls):
            raise Exception("CreateUI failed: return {} is not {}".format(n, cls))
        return n

    @classmethod
    def PushUI(cls, params={}):
        # params["isHud"] = int(isHud)
        n = clientApi.PushScreen(GetModName(), cls._key, params)
        if not isinstance(n, cls):
            raise Exception("CreateUI failed: return {} is not {}".format(n, cls))
        return n

    def RemoveUI(self):
        self._deactive()
        self.SetRemove()

    # ==== overload ====

    def Create(self):
        """ 超类方法用于激活页面。 """
        self._active()

    def Destroy(self):
        """ 超类方法用于反激活页面。 """
        self._deactive()
        for element in self._elem_cacher.values():
            element.callDestroy()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        pass


    # ====

    def AddElement(self, ctrl_def_name, ctrl_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        return UBaseCtrl(self, addElement(self, ctrl_def_name, ctrl_name, None, force_update))

    def GetElement(self, path):
        # type: (str | SNode) -> UBaseCtrl
        if isinstance(path, SNode):
            path = path.base
        return self._get_elem_cache(path)

    def AddDynamicBinding(self, func, binding_name):
        uid = uuid.uuid4().hex
        patch_name = '{}_patch_{}'.format(uid, func.im_func.func_name)
        self._bind_data[func.im_func.func_name] = patch_name
        func.im_func.func_name = patch_name
        setattr(self, func.im_func.func_name, func)
        if hasattr(func, 'collection_name'):
            self._process_collection(func, self.screen_name) # type: ignore
        if hasattr(func, 'binding_flags'):
            self._process_default(func, self.screen_name) # type: ignore

    def UnBinding(self, func):
        name = self._bind_data.get(func.im_func.func_name)
        if name:
            if hasattr(func, 'collection_name'):
                self._process_collection_unregister(func, self.screen_name) # type: ignore
            if hasattr(func, 'binding_flags'):
                self._process_default_unregister(func, self.screen_name) # type: ignore
            if hasattr(self, name):
                delattr(self, name)

    # ==== unsafe methods
    # def _DynamicBindInt(self, binding_name, binding_func):
    #     import gui # pyright: ignore[reportMissingImports]
    #     gui.bind_int_handler(self.screen_name, binding_name, self, binding_func)
    #     self.__dynaBindings.append((binding_name, binding_func))

    # ==== private methods

    def _active(self):
        from .pool import _addActiveScreen
        if self.activated:
            return
        _addActiveScreen(self)
        self.activated = True

    def _deactive(self):
        from .pool import _removeActiveScreen
        if not self.activated:
            return
        _removeActiveScreen(self)
        self.activated = False
        if clientApi.GetTopUINode() is self:
            clientApi.PopScreen()


    __getitem__ = __gt__ = GetElement

    def _get_elem_cache(self, path):
        # type: (str) -> UBaseCtrl
        if path in self._elem_cacher:
            return self._elem_cacher[path]
        else:
            ui = UBaseCtrl(self, self.GetBaseUIControl(path))
            self._elem_cacher[path] = ui
            return ui

    # ==== unsafe private methods

__all__ = [
    "UScreenNode"
]
