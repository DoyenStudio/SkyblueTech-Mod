# coding=utf-8

from skybluetech_scripts.skybluetech.common.events.machinery.assembler import (
    ACTION_PULL_UPGRADER,
    ACTION_PUSH_UPGRADER,
    AssemblerActionRequest,
    AssemblerUpgradersUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.assembler import (
    RF_MAX,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
UPGRADERS_LIST_PATH = MAIN_PATH / "upgraders_view"


@RegistToolDeltaScreen("AssemblerUI.main", is_proxy=True)
class AssemblerUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power = self.GetElement(POWER_PATH)
        self.upgraders_grid = (
            self.GetElement(UPGRADERS_LIST_PATH).asScrollView().GetContent().asGrid()
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

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        storage_rf = GetValue(data, K_STORE_RF, 0)
        UpdatePowerBar(self.power, storage_rf, RF_MAX)

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
