# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.mini_miner import MiniMinerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import (
    UpdatePowerBar,
    InitFluidDisplay,
    UpdateFluidDisplay,
)

POWER_NODE = MAIN_PATH / "power_bar"
FLUID_NODE = MAIN_PATH / "fluid_display"
INFO_LABEL_NODE = MAIN_PATH / "panel_bg/info_label"


@RegistToolDeltaScreen("MiniMinerUI.main", is_proxy=True)
class MiniMinerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = MiniMinerUISync.NewClient(dim, x, y, z)  # type: MiniMinerUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.info_label = self.GetElement(INFO_LABEL_NODE).asLabel()
        self.power_bar = self.GetElement(POWER_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.update_cb = InitFluidDisplay(
            self.fluid_display,
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            ),
        )

    def WhenUpdated(self):
        if not self.inited:
            return
        self.update_cb()
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFluidDisplay(
            self.fluid_display,
            self.sync.fluid_id,
            self.sync.fluid_volume,
            self.sync.max_volume,
        )
        dx, dy, dz = self.sync.digging_pos
        self.info_label.SetText(
            "正在挖掘： (%d, %d, %d)\n\n%s"
            % (
                dx,
                dy,
                dz,
                self.sync.WorkMode.zh_cn(self.sync.work_mode),
            )
        )
