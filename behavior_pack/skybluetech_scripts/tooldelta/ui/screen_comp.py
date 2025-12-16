# coding=utf-8

import mod.client.extraClientApi as clientApi
from ..internal import GetModName
from ..events.client.control import OnKeyPressInGame
from .utils import SNode
from .elem_comp import UBaseCtrl
from .functions import addElement


ScreenNode = clientApi.GetScreenNodeCls()


class UScreenNode(ScreenNode):
    bound_ui = None # type: str | None
    _key = "???"
    top_node = None # type: SNode | None

    def __init__(self, *args, **kwargs):
        ScreenNode.__init__(self, *args, **kwargs)
        self.base = self
        self.activated = False
        self._elem_cacher = {} # type: dict[str, UBaseCtrl]
        self._vars = {}

    @classmethod
    def CreateUI(cls, params={}):
        # type: (dict) -> UScreenNode
        # params["isHud"] = int(isHud)
        n = clientApi.PushScreen(GetModName(), cls._key, params)
        if not isinstance(n, cls):
            raise Exception("CreateUI failed: return {} is not {}".format(n, cls))
        return n

    def RemoveUI(self):
        self._deactive()
        

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


    # ==== overload ====

    def OnUReactive(self):
        # type: () -> None
        "超类方法, 覆写后在重新激活 UI 时被调用"
        pass

    def OnUDeactive(self):
        # type: () -> None
        "超类方法, 覆写后在取消激活 UI 时被调用"
        pass

    def Create(self):
        """ 超类方法用于激活页面。 """
        self._active()

    def Destroy(self):
        """ 超类方法用于反激活页面。 """
        for element in self._elem_cacher.values():
            element.callDestroy()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        pass


    # ====

    def GetElement(self, path):
        # type: (str | SNode) -> UBaseCtrl
        if isinstance(path, SNode):
            path = path.base
        return self._get_elem_cache(path)

    __getitem__ = __gt__ = GetElement

    def _get_elem_cache(self, path):
        # type: (str) -> UBaseCtrl
        if path in self._elem_cacher:
            return self._elem_cacher[path]
        else:
            ui = UBaseCtrl(self, self.GetBaseUIControl(path))
            self._elem_cacher[path] = ui
            return ui

__all__ = [
    "UScreenNode"
]
