# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.pump import PumpUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, InitFluidDisplay

POWER_NODE = MAIN_PATH / "power_bar"
FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("PumpUI.main", is_proxy=True)
class PumpUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = PumpUISync.NewClient(dim, x, y, z)  # type: PumpUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.fluid_updater = InitFluidDisplay(
            self.fluid_display,
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            ),
        )
        self.sync.SetUpdateCallback(self.WhenUpdated)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.fluid_updater()
