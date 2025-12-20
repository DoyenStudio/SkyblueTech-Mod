# coding=utf-8

from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistProxyScreen, ViewBinder
from skybluetech_scripts.tooldelta.api.timer import Delay, ExecLater
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from skybluetech_scripts.tooldelta.events.notify import NotifyToServer
from ...define.events.assembler import *
from ...ui_sync.machines.assembler import AssemblerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"
UPGRADERS_LIST_NODE = MAIN_PATH / "upgraders_view"

event_cbs = set()


@RegistProxyScreen("AssemblerUI.main")
class AssemblerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = AssemblerUISync.NewClient(dim, x, y, z) # type: AssemblerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power = self.GetElement(POWER_NODE)
        self.upgraders_grid = self.GetElement(UPGRADERS_LIST_NODE).asScrollView().GetContent().asGrid()
        self[MAIN_PATH / "push_btn"].asButton().SetCallback(self.onPush)
        MachinePanelUIProxy.OnCreate(self)
        event_cbs.add(self.onListUpdate)

    def OnDestroy(self):
        event_cbs.discard(self.onListUpdate)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#upgrade_arg_click") # pyright: ignore[reportOptionalCall]
    def onclick(self, arg):
        _, x, y, z = self.pos
        NotifyToServer(AssemblerActionRequest(x, y, z, ACTION_PULL_UPGRADER, arg["#collection_index"]))

    def onPush(self, _):
        _, x, y, z = self.pos
        NotifyToServer(AssemblerActionRequest(x, y, z, ACTION_PUSH_UPGRADER, 0))

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power, self.sync.storage_rf, self.sync.rf_max)

    def onListUpdate(self, event):
        # type: (AssemblerUpgradersUpdate) -> None
        lis = event.lis
        siz = len(lis)
        self.upgraders_grid.SetGridDimension((1, siz))
        if siz != self.upgraders_grid.GetGridDimension()[1]:
            self.upgraders_grid.ExecuteAfterUpdate(lambda :self.updateLater(lis))
        else:
            ExecLater(0, lambda: self.updateLater(lis))
        

    def updateLater(self, lis):
        # type: (list[tuple[str, str, int]]) -> None
        for i, (typ, text, count) in enumerate(lis):
            if count != -1:
                text = GetItemHoverName(text)
            elem = self.upgraders_grid.GetGridItem(0, i)
            elem["text"].asLabel().SetText(text)
            elem["item"].asItemRenderer().SetUiItem(Item(typ))


@AssemblerUpgradersUpdate.Listen()
@Delay(0.1)
def onOrigListUpdate(event):
    # type: (AssemblerUpgradersUpdate) -> None
    onListUpdate(event, 0)

def onListUpdate(event, exec_depth):
    # type: (AssemblerUpgradersUpdate, int) -> None
    if exec_depth > 5:
        print("[WARNING] AssemblerUI.onListUpdate: Too many retries")
        return
    if event_cbs:
        for cb in event_cbs:
            cb(event)
    else:
        ExecLater(0.1, onListUpdate, event, exec_depth + 1)
