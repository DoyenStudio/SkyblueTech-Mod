# coding=utf-8
#
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.api.client.player import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.api.timer import ExecLater
from skybluetech_scripts.tooldelta.events.notify import NotifyToServer
from skybluetech_scripts.tooldelta.events import CustomC2SEvent
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
    OnKeyPressInGame,
)
from skybluetech_scripts.tooldelta.ui import SCREEN_BASE_PATH, ToolDeltaScreen
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


class MachinePanelUI(ToolDeltaScreen):
    EXIT_BTN_PATH = "/ExitBtn"

    def __init__(self, namespace, name, param):
        ToolDeltaScreen.__init__(self, namespace, name, param)
        self.inited = False
        self.sync = None  # type: S2CSync | None
        self.dim, self.x, self.y, self.z = self.get_bound_pos()

    def get_bound_pos(self):
        # type: () -> tuple[int, int, int, int]
        return self._init_params["st:dmpos"]

    def _on_create(self):
        self[self.EXIT_BTN_PATH].asButton().SetCallback(self.OnExit)
        self.inited = True
        if self.sync:
            self.sync.Activate()

    def _on_destroy(self):
        """超类方法, 告诉服务端 UI 关闭。"""
        if self.sync:
            self.sync.Deactivate()

    def OnExit(self, params):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0.1, self.RemoveUI)


class MachinePanelUIProxy(ToolDeltaScreen):
    def __init__(self, screenName, screenNode):
        global GPlayerId, GPos
        ToolDeltaScreen.__init__(self, screenName, screenNode)
        self.sync = None  # type: S2CSync | None
        if GPos is None:
            raise RuntimeError("Player do not click machine but create UI")
        self.pid = GPlayerId
        self.pos = GPos

    def _on_create(self):
        ToolDeltaScreen._on_create(self)
        self.inited = True
        if self.sync:
            self.sync.Activate()

    def _on_destroy(self):
        ToolDeltaScreen._on_destroy(self)
        if self.sync:
            self.sync.Deactivate()

    def OnExit(self):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0, self.RemoveUI)


GPlayerId = ""
GPos = None


@ClientBlockUseEvent.Listen()
def onCliBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    global GPlayerId, GPos
    dim = GetPlayerDimensionId()
    GPlayerId = event.playerId
    GPos = (dim, int(event.x), int(event.y), int(event.z))
