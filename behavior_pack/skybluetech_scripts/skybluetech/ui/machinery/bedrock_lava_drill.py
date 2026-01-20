# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ...ui_sync.machinery.bedrock_lava_drill import BedrockLavaDrillUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateFluidDisplay

POWER_NODE = MAIN_PATH / "power_bar"
FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("BedrockLavaDrillUI.main", is_proxy=True)
class BedrockLavaDrillUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = BedrockLavaDrillUISync.NewClient(dim, x, y, z) # type: BedrockLavaDrillUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.sync.WhenUpdated = self.WhenUpdated

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFluidDisplay(
            self.fluid_display,
            self.sync.fluid_id,
            self.sync.fluid_volume,
            self.sync.max_volume,
        )

