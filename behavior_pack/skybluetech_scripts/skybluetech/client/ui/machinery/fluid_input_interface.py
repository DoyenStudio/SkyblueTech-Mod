# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.fluid_interface import FluidInterfaceUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import InitFluidDisplay

FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("FluidInputInterfaceUI.main", is_proxy=True)
class FluidInputInterfaceUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FluidInterfaceUISync.NewClient(dim, x, y, z)  # type: FluidInterfaceUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.fluid_updater = InitFluidDisplay(
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
        self.fluid_updater()
