# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.api.client import NewSingleBlockPalette, CombineBlockPaletteToGeometry
from ...ui_sync.machines.hydroponic_base import HydroponicBaseUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import InitFluidDisplay

FLUID_0_NODE = MAIN_PATH / "fluid0"
FLUID_1_NODE = MAIN_PATH / "fluid1"


@RegistToolDeltaScreen("HydroponicBaseUI.main", is_proxy=True)
class HydroponicBaseUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = HydroponicBaseUISync.NewClient(dim, x, y, z) # type: HydroponicBaseUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.fluid_0 = self.GetElement(FLUID_0_NODE)
        self.fluid_1 = self.GetElement(FLUID_1_NODE)
        self.fluid_0_updater = InitFluidDisplay(
            self.fluid_0,
            lambda: (
                self.sync.fluid_1_type,
                self.sync.fluid_1_volume,
                self.sync.fluid_1_max_volume,
            )
        )
        self.fluid_1_updater = InitFluidDisplay(
            self.fluid_1,
            lambda: (
                self.sync.fluid_2_type,
                self.sync.fluid_2_volume,
                self.sync.fluid_2_max_volume,
            )
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_0_updater()
        self.fluid_1_updater()

