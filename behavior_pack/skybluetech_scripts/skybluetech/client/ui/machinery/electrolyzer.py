# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF, FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electrolyzer import (
    FLUID_SLOT_MAX_VOLUMES, STORE_RF_MAX, recipes,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.client.ui.machinery_extra_pages import (
    FluidPipeSettingsPage,
)
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import AsRecipeCheckerBtn
from skybluetech_scripts.skybluetech.client.ui.machinery.define_ex import (
    MAIN_PATH, MachinePanelUIProxyEx,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import (
    FluidDisplayer, UpdatePowerBar,
)


@RegistToolDeltaScreen("ElectrolyzerUI.main", is_proxy=True)
class ElectrolyzerUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.fluid_displayers = [
            FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot)))
            for slot in range(4)
        ]
        recipe_button = self.GetElement(MAIN_PATH / "recipe_check_btn").asButton()
        if len(recipes) > 0:
            AsRecipeCheckerBtn(recipe_button, recipes)
        else:
            # The recipe checker rejects empty collections.
            recipe_button.SetVisible(False)

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        for slot, displayer in enumerate(self.fluid_displayers):
            fluid = FluidSlotClient(data, slot)
            displayer.update(fluid.fluid_id, fluid.volume, FLUID_SLOT_MAX_VOLUMES[slot])
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)
