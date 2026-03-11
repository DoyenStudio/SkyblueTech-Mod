# coding=utf-8
#
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.digger import DiggerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
BLOCK_DISP_NODE = MAIN_PATH / "block_disp"
WORK_STATUS_NODE = MAIN_PATH / "work_status"


@RegistToolDeltaScreen("DiggerUI.main", is_proxy=True)
class DiggerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = DiggerUISync.NewClient(dim, x, y, z)  # type: DiggerUISync
        self.sync.SetWhenUpdatedCallback(self.WhenUpdated)
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.block_disp = self.GetElement(BLOCK_DISP_NODE).asItemRenderer()
        self.work_status = self.GetElement(WORK_STATUS_NODE).asLabel()
        self.block_disp.SetUiItem(Item("minecraft:barrier"))

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
        if self.sync.block_id == "minecraft:air" or self.sync.block_id is None:
            self.sync.block_id = "minecraft:barrier"
        self.block_disp.SetUiItem(Item(self.sync.block_id, self.sync.block_aux))
        if self.sync.block_id != "minecraft:barrier":
            self.work_status.SetText(
                "当前正在挖掘 " + GetItemHoverName(self.sync.block_id)
            )
        else:
            self.work_status.SetText("当前无可挖掘方块")
