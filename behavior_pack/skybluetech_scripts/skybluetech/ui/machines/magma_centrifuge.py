# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.magma_centrifuge import MagmaCentrifugeUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, InitFluidsDisplay

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
LEFT_FLUID = MAIN_PATH / "left_fluid"
RIGHT_FLUID = MAIN_PATH / "right_fluid"


@RegistProxyScreen("MagmaCentrifugeUI.main")
class MagmaCentrifugeUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = MagmaCentrifugeUISync.NewClient(dim, x, y, z) # type: MagmaCentrifugeUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.left_fluid_updater = self.GetElement(LEFT_FLUID)
        self.right_fluid_updaters = [self > (RIGHT_FLUID + str(i + 1)) for i in range(6)]
        self.update_cbs = [InitFluidsDisplay(self.left_fluid_updater, self.sync.fluids, 0)]
        for i, ui in enumerate(self.right_fluid_updaters):
            self.update_cbs.append(InitFluidsDisplay(ui, self.sync.fluids, i + 1))
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
        for cb in self.update_cbs:
            cb()

