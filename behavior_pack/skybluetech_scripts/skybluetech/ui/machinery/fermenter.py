# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ...define.events.machinery.fermenter import FermenterSetTemperatureEvent, FermenterSeMaxVolumeEvent
from ...define.flags import DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
from ...machinery_def.fermenter import spec_recipes, TEMPERATURE_MIN, TEMPERATURE_MAX, POOL_MAX_VOLUME
from ...ui_sync.machinery.fermenter import FermenterUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, InitFluidDisplay, UpdateImageTransformColor

FLAG_OK = 0

POWER_NODE = MAIN_PATH / "power_bar"
OUT_GAS_DISP_NODE = MAIN_PATH / "out_gas_display"
OUT_FLUID_DISP_NODE = MAIN_PATH / "out_fluid_display"
POOL_IMG_NODE = MAIN_PATH / "pool/fluid_img"
TEMPERATURE_LABEL_NODE = MAIN_PATH / "temp_label"
EXPECTED_TEMPERATURE_LABEL_NODE = MAIN_PATH / "expected_temp_label"
POOL_TIP_LABEL_NODE = MAIN_PATH / "pool_tip"
LACK_BLOCKS_TIP_NODE = MAIN_PATH / "lack_blocks_tip"
TEMPERATURE_SLIDER_NODE = MAIN_PATH / "slider"
MAX_VOLUME_BAR_NODE = MAIN_PATH / "pool/max_volume_bar"
VOLUME_SLIDER_NODE = MAIN_PATH / "volume_slider"


@RegistToolDeltaScreen("FermenterUI.main", is_proxy=True)
class FermenterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FermenterUISync.NewClient(dim, x, y, z) # type: FermenterUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.out_gas_display = self.GetElement(OUT_GAS_DISP_NODE)
        self.out_fluid_display = self.GetElement(OUT_FLUID_DISP_NODE)
        self.pool_img = self.GetElement(POOL_IMG_NODE).asImage()
        self.temperature_label = self.GetElement(TEMPERATURE_LABEL_NODE).asLabel()
        self.expected_temperature_label = self.GetElement(EXPECTED_TEMPERATURE_LABEL_NODE).asLabel()
        self.pool_tip = self.GetElement(POOL_TIP_LABEL_NODE).asLabel()
        self.lack_blocks_tip = self.GetElement(LACK_BLOCKS_TIP_NODE).asLabel()
        self.temperature_slider = self.GetElement(TEMPERATURE_SLIDER_NODE).asSlider()
        self.volume_slider = self.GetElement(VOLUME_SLIDER_NODE).asSlider()
        self.volume_bar = self.GetElement(MAX_VOLUME_BAR_NODE).asImage()
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

    def WhenUpdated(self):
        if not self.inited:
            return
        self.out_gas_updat_updater()
        self.out_fluid_updat_updater()
        UpdatePowerBar(self.power_bar, self.sync.store_rf, self.sync.store_rf_max)
        recipe = spec_recipes.get(self.sync.recipe_id)
        if recipe is None:
            r, g, b = 0, 0xa6, 0xff,
        else:
            color = recipe.color
            r, g, b = (color >> 16 & 0xff, color >> 8 & 0xff, color & 0xff)
        UpdateImageTransformColor(
            self.pool_img,
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
        self.volume_bar.SetFullPos(
            "y",
            UICtrlPosData(
                "parent",
                relative_value=0.5-self.sync.expected_water_max_volume/POOL_MAX_VOLUME
            )
        )
        self.volume_slider.SetSliderValue(
            1-self.sync.expected_water_max_volume/POOL_MAX_VOLUME
        )
        self.pool_img.SetFullSize("y", UICtrlPosData("parent", relative_value=self.sync.content_volume_pc))
        sstatus = self.sync.structure_status
        if sstatus == FLAG_OK:
            self.pool_tip.SetText("发酵池 （就绪）")
        elif sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            self.pool_tip.SetText("发酵池 （缺少必要模块）")
        else:
            self.pool_tip.SetText("发酵池 （结构不完整）")
        if self.sync.structure_lack_blocks and sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            fmt = "§l§4结构缺失必须组件：\n" + "\n".join(
                GetItemHoverName(k) + "§l§4 x" + str(v)
                for k, v in self.sync.structure_lack_blocks.items()
            )
            self.lack_blocks_tip.SetText(fmt)
        else:
            if self.sync.recipe_id == 0:
                fmt = "§l§0无配方"
            else:
                recipe = spec_recipes[self.sync.recipe_id]
                fmt = (
                    # "§0§3发酵液量： §0%smB" % self.sync.mu
                    # + "\n"
                    "§3菌群浓度： §0%.1f%%%%" % (self.sync.mud_thickness * 100)
                    + "\n"
                    + "§2将产出： §5%s§0、 §3%s" % (
                        GetItemHoverName(recipe.out_gas_id),
                        GetItemHoverName(recipe.out_fluid_id),
                    )
                    + "\n"
                    + (
                        "§4未达到最低产出浓度"
                        if self.sync.mud_thickness < recipe.produce_thickness
                        else "§2生产中： %.1fmB/s； %.1fmB/s" % (
                            self.sync.gas_product_speed,
                            self.sync.fluid_product_speed,
                        )
                    )
                )
            self.lack_blocks_tip.SetText(fmt)
        
    @Binder.binding(Binder.BF_SliderFinished | Binder.BF_SliderFinished, "#fermenter.temperature_set_ok")
    def onTemperatureSliderFinished(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        temp = TEMPERATURE_MIN + (TEMPERATURE_MAX - TEMPERATURE_MIN) * progress
        self.expected_temperature_label.SetText("控温 %.1f°C" % temp)
        if finished:
            FermenterSetTemperatureEvent(x, y, z, temp).send()

    @Binder.binding(Binder.BF_SliderChanged | Binder.BF_SliderFinished, "#fermenter.volume_setter")
    def onTemperatureSliderChanged(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        vol = (1-progress) * POOL_MAX_VOLUME
        if finished:
            FermenterSeMaxVolumeEvent(x, y, z, vol).send()

