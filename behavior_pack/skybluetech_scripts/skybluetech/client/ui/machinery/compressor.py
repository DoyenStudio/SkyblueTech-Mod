# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.compressor import CompressorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R

from ..recipe_checker import AsRecipeCheckerBtn
from ....common.machinery_def.compressor import recipes

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"


@RegistToolDeltaScreen("CompressorUI.main", is_proxy=True)
class CompressorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = CompressorUISync.NewClient(dim, x, y, z)  # type: CompressorUISync
        self.sync.SetWhenUpdatedCallback(self.WhenUpdated)
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,  # pyright: ignore[reportArgumentType]
        )

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
