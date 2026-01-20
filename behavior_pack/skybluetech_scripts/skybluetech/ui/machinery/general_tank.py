# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ...ui_sync.machinery.general_tank import GeneralTankUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import InitFluidDisplay, UpdateFluidDisplay

FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("GeneralTankUI.main", is_proxy=True)
class GeneralTankUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = GeneralTankUISync.NewClient(dim, x, y, z) # type: GeneralTankUISync
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.sync.WhenUpdated = self.WhenUpdated
        self.fluid_updater = InitFluidDisplay(
            self.fluid_display, lambda :(
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            )
        )

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_updater()

