# coding=utf-8
#
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.api.client.player import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.api.timer import ExecLater
from skybluetech_scripts.tooldelta.events.notify import NotifyToServer
from skybluetech_scripts.tooldelta.events import CustomC2SEvent
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent, OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import SNode, SCREEN_BASE_PATH
from skybluetech_scripts.tooldelta.ui.screen_comp import UScreenNode
from skybluetech_scripts.tooldelta.ui.proxy_screen import UScreenProxy
from skybluetech_scripts.tooldelta.extensions.ui_sync import S2CSync

KeyEnum = GetMinecraftEnum().KeyBoardType
_ESCAPE = KeyEnum.KEY_ESCAPE
MAIN_PATH = SCREEN_BASE_PATH / "root_panel/bg/main"


class UIOpen(CustomC2SEvent):
    name = "skybluetech:UIOpen"

    def __init__(self, ui_key):
        # type: (str) -> None
        self.ui_key = ui_key

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]

    def marshal(self):
        return {"uiKey": self.ui_key}


class UIClose(CustomC2SEvent):
    name = "skybluetech:UIClose"

    def __init__(self, ui_key):
        # type: (str) -> None
        self.ui_key = ui_key

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]

    def marshal(self):
        return {"uiKey": self.ui_key}


class MachinePanelUI(UScreenNode):
    EXIT_BTN_PATH = "/ExitBtn"

    def __init__(self, namespace, name, param):
        UScreenNode.__init__(self, namespace, name, param)
        self.inited = False
        self.sync = None # type: S2CSync | None
    
    def Create(self):
        """ 超类方法, 告诉服务端 UI 开启的同时创建一个退出按钮回调。 """
        UScreenNode.Create(self)
        self[self.EXIT_BTN_PATH].asButton().SetCallback(self.OnExit)
        NotifyToServer(UIOpen(self._key))
        self.inited = True
        if self.sync:
            self.sync.Activate()
    
    def Destroy(self):
        """ 超类方法, 告诉服务端 UI 关闭。 """
        UScreenNode.Destroy(self)
        NotifyToServer(UIClose(self._key))
        if self.sync:
            self.sync.Deactivate()

    def OnExit(self, params):
        self._exitLater()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        UScreenNode.OnCurrentPageKeyEvent(self, event)
        if event.key == _ESCAPE:
            self._exitLater()

    def _exitLater(self):
        ExecLater(0.1, self.RemoveUI)



class MachinePanelUIProxy(UScreenProxy):
    def __init__(self, screenName, screenNode):
        global GPlayerId, GPos
        UScreenProxy.__init__(self, screenName, screenNode)
        self.sync = None # type: S2CSync | None
        if GPos is None:
            raise RuntimeError("Player do not click machine but create UI")
        self.pid = GPlayerId
        self.pos = GPos
    
    def OnCreate(self):
        """ 超类方法, 告诉服务端 UI 开启的同时创建一个退出按钮回调。 """
        UScreenProxy.OnCreate(self)
        NotifyToServer(UIOpen(self.bound_proxier))
        self.inited = True
        if self.sync:
            self.sync.Activate()

    def OnDestroy(self):
        """ 超类方法, 告诉服务端 UI 关闭。 """
        UScreenProxy.OnDestroy(self)
        NotifyToServer(UIClose(self.bound_proxier))
        if self.sync:
            self.sync.Deactivate()

    def OnExit(self):
        self._exitLater()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        UScreenProxy.OnCurrentPageKeyEvent(self, event)
        if event.key == _ESCAPE:
            return
            self.OnExit()

    def _exitLater(self):
        ExecLater(0, self.RemoveUI)


GPlayerId = ''
GPos = None

@ClientBlockUseEvent.Listen()
def onCliBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    global GPlayerId, GPos
    dim = GetPlayerDimensionId()
    GPlayerId = event.playerId
    GPos = (dim, int(event.x), int(event.y), int(event.z))
