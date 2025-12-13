# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen, ViewBinder
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ...define.events.fermenter import FermenterSetTemperatureEvent
from ...define.flags import DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
from ...define.machine_config.fermenter import spec_recipes, TEMPERATURE_MIN, TEMPERATURE_MAX
from ...ui_sync.machines.fermenter import FermenterUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from ..utils import UpdatePowerBar, InitFluidDisplay, UpdateImageTransformColor

FLAG_OK = 0

POWER_NODE = MAIN_PATH / "power_bar"
OUT_GAS_DISP_NODE = MAIN_PATH / "out_gas_display"
OUT_FLUID_DISP_NODE = MAIN_PATH / "out_fluid_display"
POOL_IMG_NODE = MAIN_PATH / "pool/fluid_img"
TEMPERATURE_LABEL_NODE = MAIN_PATH / "temp_label"
EXPECTED_TEMPERATURE_LABEL_NODE = MAIN_PATH / "expected_temp_label"
POOL_TIP_LABEL_NODE = MAIN_PATH / "pool_tip"
LACK_BLOCKS_TIP_NODE = MAIN_PATH / "lack_blocks_tip"
TEMPERATURE_SLIDE_BAR_NODE = MAIN_PATH / "slider"


@RegistProxyScreen("FermenterUI.main")
class FermenterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FermenterUISync.NewClient(dim, x, y, z) # type: FermenterUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.out_gas_display = self.GetElement(OUT_GAS_DISP_NODE)
        self.out_fluid_display = self.GetElement(OUT_FLUID_DISP_NODE)
        self.pool_img = self.GetElement(POOL_IMG_NODE).AsImage()
        self.temperature_label = self.GetElement(TEMPERATURE_LABEL_NODE).AsLabel()
        self.expected_temperature_label = self.GetElement(EXPECTED_TEMPERATURE_LABEL_NODE).AsLabel()
        self.pool_tip = self.GetElement(POOL_TIP_LABEL_NODE).AsLabel()
        self.lack_blocks_tip = self.GetElement(LACK_BLOCKS_TIP_NODE).AsLabel()
        self.temperature_slider = self.GetElement(TEMPERATURE_SLIDE_BAR_NODE).AsSlider()
        self.out_gas_updat_updater = InitFluidDisplay(
            self.out_gas_display, 
            lambda: (
                self.sync.out_gas_id,
                self.sync.out_gas_volume,
                self.sync.out_gas_max_volume,
            )
        )
        self.out_fluid_updat_updater = InitFluidDisplay(
            self.out_fluid_display, 
            lambda: (
                self.sync.out_fluid_id,
                self.sync.out_fluid_volume,
                self.sync.out_fluid_max_volume,
            )
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.out_gas_updat_updater()
        self.out_fluid_updat_updater()
        UpdatePowerBar(self.power_bar, self.sync.store_rf, self.sync.store_rf_max)
        recipe = spec_recipes.get(self.sync.recipe_id)
        if recipe is None:
            r, g, b = 0xff, 0xff, 0xff
        else:
            color = recipe.color
            r, g, b = (color >> 16 & 0xff, color >> 8 & 0xff, color & 0xff)
        UpdateImageTransformColor(
            self.pool_img.AsImage(),
            0, 0xa6, 0xff,
            r, g, b,
            self.sync.mud_thickness,
        )
        self.temperature_slider.SetSliderValue(
            (self.sync.expected_temperature - TEMPERATURE_MIN)
            /
            (TEMPERATURE_MAX - TEMPERATURE_MIN)
        )
        self.temperature_label.SetText("酵温 %.1f°C" % self.sync.mud_temperature)
        self.expected_temperature_label.SetText("控温 %.1f°C" % self.sync.expected_temperature)
        self.pool_img.SetFullSize("y", {"followType": "parent", "relativeValue": self.sync.content_volume_pc})
        sstatus = self.sync.structure_status
        if sstatus == FLAG_OK:
            self.pool_tip.SetText("发酵池 （就绪）")
        elif sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            self.pool_tip.SetText("发酵池 （缺少必要模块）")
        else:
            self.pool_tip.SetText("发酵池 （结构不完整）")
        if self.sync.structure_lack_blocks and sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            fmt = "§l§4结构缺失方块：\n" + "\n".join(
                GetItemHoverName(k) + "§l§4 x" + str(v)
                for k, v in self.sync.structure_lack_blocks.items()
            )
            self.lack_blocks_tip.SetText(fmt)
        else:
            self.lack_blocks_tip.SetText("")
        
    @ViewBinder.binding(ViewBinder.BF_SliderFinished, "#fermenter.temperature_set_ok") # pyright: ignore[reportOptionalCall]
    def onTemperatureSliderFinished(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        temp = TEMPERATURE_MIN + (TEMPERATURE_MAX - TEMPERATURE_MIN) * progress
        FermenterSetTemperatureEvent(x, y, z, temp).send()

    @ViewBinder.binding(ViewBinder.BF_SliderChanged, "#fermenter.temperature_set_ok") # pyright: ignore[reportOptionalCall]
    def onTemperatureSliderChanged(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        temp = TEMPERATURE_MIN + (TEMPERATURE_MAX - TEMPERATURE_MIN) * progress
        self.expected_temperature_label.SetText("控温 %.1f°C" % temp)
