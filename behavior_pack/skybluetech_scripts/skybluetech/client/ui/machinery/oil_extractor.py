# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.define.id_enum.machinery import OIL_EXTRACTOR
from ....common.ui_sync.machinery.oil_extractor import OilExtractorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, InitFluidDisplay

from ..recipe_checker import AsRecipeCheckerBtn
from ....common.machinery_def.oil_extractor import recipes

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("OilExtractorUI.main", is_proxy=True)
class OilExtractorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = OilExtractorUISync.NewClient(dim, x, y, z)  # type: OilExtractorUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.fluid_updater = InitFluidDisplay(
            self.fluid_display,
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            ),
        )
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            OIL_EXTRACTOR,
            recipes,  # pyright: ignore[reportArgumentType]
        )

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_updater()
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
