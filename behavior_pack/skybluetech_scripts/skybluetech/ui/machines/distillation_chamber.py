# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, ViewBinder
from ...ui_sync.machines.distillation_chamber import DistillationChamberUISync
from ...utils.fmt import FormatKelvin, FormatFluidVolume
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import InitFluidDisplay

from ..recipe_checker import AsRecipeCheckerBtn
from ...machinery_def.distillation_chamber import recipes

TEMPERATURE_NODE = MAIN_PATH / "right_board/temp_disp"
RATE_NODE = MAIN_PATH / "right_board/rate_disp"
LOWER_FLUID_NODE = MAIN_PATH / "lower_fluid"
UPPER_FLUID_NODE = MAIN_PATH / "upper_fluid"


@RegistToolDeltaScreen("DistillationChamberUI.main", is_proxy=True)
class DistillationChamberUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = DistillationChamberUISync.NewClient(dim, x, y, z)  # type: DistillationChamberUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.upper_fluid = self.GetElement(UPPER_FLUID_NODE)
        self.lower_fluid = self.GetElement(LOWER_FLUID_NODE)
        self.temperature_label = self.GetElement(TEMPERATURE_NODE).asLabel()
        self.rate_label = self.GetElement(RATE_NODE).asLabel()
        self.fluid_updater1 = InitFluidDisplay(
            self.lower_fluid,
            lambda: (
                self.sync.lower_fluid_id,
                self.sync.lower_fluid_volume,
                self.sync.lower_fluid_max_volume,
            )
        )
        self.fluid_updater2 = InitFluidDisplay(
            self.upper_fluid,
            lambda: (
                self.sync.upper_fluid_id,
                self.sync.upper_fluid_volume,
                self.sync.upper_fluid_max_volume,
            )
        )
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            "skybluetech:distillation_chamber",
            recipes, # pyright: ignore[reportArgumentType]
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_updater1()
        self.fluid_updater2()
        self.rate_label.SetText(FormatFluidVolume(self.sync.output_rate) + "/t")
        self.temperature_label.SetText(FormatKelvin(self.sync.current_temperature))
        