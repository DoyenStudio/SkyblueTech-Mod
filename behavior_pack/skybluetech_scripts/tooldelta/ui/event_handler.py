from ..events.server.ui import CreateUIRequest, PushUIRequest, ForceRemoveUIRequest
from ..events.client.control import OnKeyPressInGame
from ..ui.reg import GetScreen
from .pool import GetActiveScreen, GetActiveScreens, GetActiveProxyScreens

@CreateUIRequest.Listen()
def onCreateUIRequest(event):
    # type: (CreateUIRequest) -> None
    ui = GetScreen(event.ui_key)
    if ui is None:
        raise ValueError("UI not found: " + event.ui_key)
    ui.CreateUI(params={"sync": event.sync_id})

@PushUIRequest.Listen()
def onPushUIRequest(event):
    # type: (PushUIRequest) -> None
    ui = GetScreen(event.ui_key)
    if ui is None:
        raise ValueError("UI not found: " + event.ui_key)
    ui.PushUI(params={"sync": event.sync_id})

@ForceRemoveUIRequest.Listen()
def onForceRemoveUIRequest(event):
    # type: (ForceRemoveUIRequest) -> None
    uiNode = GetActiveScreen(event.ui_key)
    if uiNode is None:
        return
    uiNode.RemoveUI()

@OnKeyPressInGame.Listen()
def onKeyPressInGame(event):
    # type: (OnKeyPressInGame) -> None
    for ui in GetActiveScreens() + GetActiveProxyScreens():
        ui.OnCurrentPageKeyEvent(event)
