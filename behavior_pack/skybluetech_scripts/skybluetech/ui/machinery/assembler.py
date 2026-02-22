# coding=utf-8

from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ...define.events.machinery.assembler import *
from ...ui_sync.machinery.assembler import AssemblerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"
UPGRADERS_LIST_NODE = MAIN_PATH / "upgraders_view"


@RegistToolDeltaScreen("AssemblerUI.main", is_proxy=True)
class AssemblerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = AssemblerUISync.NewClient(dim, x, y, z)  # type: AssemblerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power = self.GetElement(POWER_NODE)
        self.upgraders_grid = (
            self.GetElement(UPGRADERS_LIST_NODE).asScrollView().GetContent().asGrid()
        )
        self[MAIN_PATH / "push_btn"].asButton().SetCallback(self.onPush)

    @Binder.binding(Binder.BF_ButtonClickUp, "#upgrade_arg_click")
    def onclick(self, arg):
        _, x, y, z = self.pos
        AssemblerActionRequest(
            x, y, z, ACTION_PULL_UPGRADER, arg["#collection_index"]
        ).send()

    def onPush(self, _):
        _, x, y, z = self.pos
        AssemblerActionRequest(x, y, z, ACTION_PUSH_UPGRADER, 0).send()

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power, self.sync.storage_rf, self.sync.rf_max)

    @MachinePanelUIProxy.Listen(AssemblerUpgradersUpdate)
    def onListUpdate(self, event):
        # type: (AssemblerUpgradersUpdate) -> None
        lis = event.lis
        siz = len(lis)
        self.upgraders_grid.SetDimensionAndCall((1, siz), lambda: self.updateLater(lis))

    def updateLater(self, lis):
        # type: (list[tuple[str, str, int]]) -> None
        for i, (typ, text, count) in enumerate(lis):
            if count != -1:
                text = GetItemHoverName(text)
            elem = self.upgraders_grid.GetGridItem(0, i)
            elem["text"].asLabel().SetText(text)
            elem["item"].asItemRenderer().SetUiItem(Item(typ))
