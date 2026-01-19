# coding=utf-8
#

import mod.client.extraClientApi as clientApi
from mod.client.ui.screenNode import ScreenNode
from mod_log import logger
from ..events.client.control import OnKeyPressInGame
from .elem_comp import UBaseCtrl
from .utils import UIPath


CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()


class UScreenProxy(CustomUIScreenProxy):
    "已废弃, 请使用 ToolDeltaScreen。"
    bound_proxier = ""

    def __init__(self, screenName, screenNode):
        # type: (str, ScreenNode) -> None
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.screenName = screenName
        self.base = self.screenNode = screenNode
        self._elem_cacher = {} # type: dict[str, UBaseCtrl]
        self.activated = False
        self._vars = {}

    def RemoveUI(self):
        self._deactive()

    def _active(self):
        from .pool import _addActiveProxyScreen
        if self.activated:
            return
        _addActiveProxyScreen(self)
        self.activated = True

    def _deactive(self):
        from .pool import _removeActiveProxyScreen
        if not self.activated:
            return
        _removeActiveProxyScreen(self)
        # self.activated = False
        if clientApi.GetTopUINode() is self.screenNode:
            clientApi.PopTopUI()


    # ==== overload ====

    def OnUReactive(self):
        # type: () -> None
        "超类方法, 覆写后在重新激活 UI 时被调用"
        pass

    def OnUDeactive(self):
        # type: () -> None
        "超类方法, 覆写后在取消激活 UI 时被调用"
        pass

    def OnCreate(self):
        """ 超类方法用于激活页面。 """
        self._active()

    def OnDestroy(self):
        """ 超类方法用于反激活页面。 """
        pass

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        pass


    # ====

    def AddElement(self, ctrl_def_name, ctrl_name, force_update=True):
        # type: (str, str, bool) -> UBaseCtrl
        return UBaseCtrl(
            self,
            self.base.CreateChildControl(ctrl_def_name, ctrl_name, None, force_update) # pyright: ignore[reportArgumentType]
        )

    def GetElement(self, path):
        # type: (str | UIPath) -> UBaseCtrl
        if isinstance(path, UIPath):
            path = path.base
        return self._get_elem_cache(path)

    # ==== private methods

    __getitem__ = __gt__ = GetElement

    def _get_elem_cache(self, path):
        # type: (str) -> UBaseCtrl
        if path in self._elem_cacher:
            return self._elem_cacher[path]
        else:
            ui = UBaseCtrl(self, self.screenNode.GetBaseUIControl(path))
            self._elem_cacher[path] = ui
            return ui
 
__all__ = [
    "UScreenProxy",
    "ViewBinder",
    "ViewRequest"
]