# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from ..machinery_extra_pages import ItemPipeSettingsPage, FluidPipeSettingsPageIndirectional
from ..recipe_checker import AsRecipeCheckerBtn
from ....common.define.flags import DEACTIVE_FLAG_NO_RECIPE, DEACTIVE_FLAG_OUTPUT_FULL
from ....common.machinery_def.basic import K_HEAT_VALUE, FluidSlotClient
from ....common.machinery_def.heat_melting_chamber import (
    MIN_KELVIN, MAX_KELVIN, OUTPUT_MAX_VOLUME, K_PROGRESS, K_DURATION,
    K_SPEED, K_OVERHEATED, recipes,
)
from ....common.utils.phys_math import Thermal
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, FormatKelvin, SetHoverText, UpdateProgress


@RegistToolDeltaScreen("HeatMeltingChamberUI.main", is_proxy=True)
class HeatMeltingChamberUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage, FluidPipeSettingsPageIndirectional)
    STATUS_TEXTS = {DEACTIVE_FLAG_NO_RECIPE: "无匹配配方或温度不足"}
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_")}

    def OnCreate(self):
        self.temperature = self.GetElement(MAIN_PATH / "temperature")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        self.fluid_displayer = FluidDisplayer(self.GetElement(MAIN_PATH / "fluid_display"))
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), recipes)

    def OnTicking(self):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block_data is None or block_data.get("exData") is None:
            return
        data = block_data["exData"]
        temperature = Thermal.GetKelvin(GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT))
        overheated = GetValue(data, K_OVERHEATED, False)
        # progress_sprite 没有 info 子控件；动态提示统一挂在带 hover_info 的温度条上。
        SetHoverText(self.temperature, "%s\n300 K ~ 900 K\n加工速度：%.2fx%s" % (
            FormatKelvin(temperature), GetValue(data, K_SPEED, 0.0),
            "\n超过最高温度：不产出流体" if overheated else ""))
        UpdateProgress(self.temperature, max(0.0, min(1.0,
            (temperature - MIN_KELVIN) / (MAX_KELVIN - MIN_KELVIN))))
        duration = max(1.0, GetValue(data, K_DURATION, 1.0))
        UpdateProgress(self.progress, min(1.0, GetValue(data, K_PROGRESS, 0.0) / duration))
        fluid = FluidSlotClient(data, 0)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, OUTPUT_MAX_VOLUME)
