from ..events.server.ui import CreateUIRequest, PushUIRequest, ForceRemoveUIRequest
from ..events.client.control import OnKeyPressInGame
from ..ui.reg import GetScreen
from .pool import GetActiveToolDeltaScreen


@CreateUIRequest.Listen()
def onCreateUIRequest(event):
    # type: (CreateUIRequest) -> None
    ui = GetScreen(event.ui_key)
    if ui is None:
        raise ValueError("UI not found: " + event.ui_key)
    ui.CreateUI(params=event.params)


@PushUIRequest.Listen()
def onPushUIRequest(event):
    # type: (PushUIRequest) -> None
    ui = GetScreen(event.ui_key)
    if ui is None:
        raise ValueError("UI not found: " + event.ui_key)
    ui.PushUI(params=event.params)


@ForceRemoveUIRequest.Listen()
def onForceRemoveUIRequest(event):
    # type: (ForceRemoveUIRequest) -> None
    uiNode = GetActiveToolDeltaScreen(event.ui_key)
    if uiNode is None:
        return
    uiNode.RemoveUI()
