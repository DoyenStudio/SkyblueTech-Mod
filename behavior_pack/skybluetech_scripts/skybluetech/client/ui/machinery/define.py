# coding=utf-8
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.api.client.player import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.api.common import ExecLater
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

class _RUNTIME:
    GPlayerId = None # type: str | None
    GPos = None # type: tuple[int, int, int, int] | None




class UIOpen(CustomC2SEvent):
    name = "skybluetech:UIOpen"

    def __init__(self, ui_key, sync_id):
        # type: (str, str) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]
        self.sync_id = data["syncId"]

    def marshal(self):
        return {"uiKey": self.ui_key, "syncId": self.sync_id}


class UIClose(CustomC2SEvent):
    name = "skybluetech:UIClose"

    def __init__(self, ui_key, sync_id):
        # type: (str, str) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]
        self.sync_id = data["syncId"]

    def marshal(self):
        return {"uiKey": self.ui_key, "syncId": self.sync_id}


class MachinePanelUI(ToolDeltaScreen):
    EXIT_BTN_PATH = "/ExitBtn"
    allow_esc_exit = False  # type: bool

    def __init__(self, namespace, name, param):
        ToolDeltaScreen.__init__(self, namespace, name, param)
        self.inited = False
        self.dim, self.x, self.y, self.z = self.get_bound_pos()
        sync_id = "machine_%d_%d_%d_%d" % (self.dim, self.x, self.y, self.z)
        self.ui_sync = S2CSync.NewClient(sync_id).Activate()

    def get_bound_pos(self):
        # type: () -> tuple[int, int, int, int]
        return self._init_params["st:dmpos"]

    def _on_create(self):
        ToolDeltaScreen._on_create(self)
        self[self.EXIT_BTN_PATH].asButton().SetCallback(self.OnExit)
        self.inited = True

    def _on_destroy(self):
        ToolDeltaScreen._on_destroy(self)
        self.ui_sync.Deactivate()

    def OnExit(self, params):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0.1, self.RemoveUI)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == _ESCAPE and self.allow_esc_exit:
            self.OnExit(None)


class MachinePanelUIProxy(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params=None):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        if _RUNTIME.GPos is None:
            raise RuntimeError("Player do not click machine but create UI")
        self.pid = _RUNTIME.GPlayerId
        self.pos = _RUNTIME.GPos
        sync_id = "machine_%d_%d_%d_%d" % _RUNTIME.GPos
        self.ui_sync = S2CSync.NewClient(sync_id)

    def _on_create(self):
        ToolDeltaScreen._on_create(self)
        self.ui_sync.Activate()
        self.inited = True

    def _on_destroy(self):
        ToolDeltaScreen._on_destroy(self)
        self.ui_sync.Deactivate()

    def OnExit(self):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0, self.RemoveUI)





@ClientBlockUseEvent.Listen()
def onClisBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    dim = GetPlayerDimensionId()
    _RUNTIME.GPlayerId = event.playerId
    _RUNTIME.GPos = (dim, int(event.x), int(event.y), int(event.z))