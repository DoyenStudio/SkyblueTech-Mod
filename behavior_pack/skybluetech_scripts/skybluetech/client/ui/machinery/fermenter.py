# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from skybluetech_scripts.skybluetech.common.events.machinery.fermenter import (
    FermenterSetTemperatureEvent,
    FermenterSeMaxVolumeEvent,
)
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_DESTROY_FLAG,
)
from skybluetech_scripts.skybluetech.common.machinery_def.fermenter import (
    spec_recipes,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
    POOL_MAX_VOLUME,
)
from skybluetech_scripts.skybluetech.common.machinery_def.fermenter import (
    K_TEMPERATURE,
    K_EXPECTED_TEMPERTURE,
    K_EXPECTED_WATER_MAX_VOLUME,
    K_MUD_VOLUME,
    K_WATER_VOLUME,
    K_MUD_VITALITY,
    K_TOTAL_VOLUME,
    K_RECIPE,
    K_CELL_HUNGER,
    K_INOCULATING_RECIPE,
    K_INOCULATE_TIME,
    K_OUTPUT_GAS_ID,
    K_OUTPUT_GAS_VOLUME,
    K_OUTPUT_GAS_MAX_VOLUME,
    K_OUTPUT_FLUID_ID,
    K_OUTPUT_FLUID_VOLUME,
    K_OUTPUT_FLUID_MAX_VOLUME,
    K_GAS_PRODUCE_SPEED,
    K_FLUID_PRODUCE_SPEED,
    K_MUD_THICKNESS,
    STORE_RF_MAX,
    POOL_MAX_VOLUME,
    spec_recipes,
    FermenterRecipe,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import (
    UpdatePowerBar,
    UpdateImageTransformColor,
    FluidDisplayer,
    GetStructureLackedBlocks,
    GetStructureLackedBlockPoses,
    FormatStructureLackedBlockPoses,
)

FLAG_OK = 0

POWER_PATH = MAIN_PATH / "power_bar"
OUT_GAS_DISP_PATH = MAIN_PATH / "out_gas_display"
OUT_FLUID_DISP_PATH = MAIN_PATH / "out_fluid_display"
POOL_IMG_PATH = MAIN_PATH / "pool/fluid_img"
TEMPERATURE_LABEL_PATH = MAIN_PATH / "temp_label"
EXPECTED_TEMPERATURE_LABEL_PATH = MAIN_PATH / "expected_temp_label"
POOL_TIP_LABEL_PATH = MAIN_PATH / "pool_tip"
LACK_BLOCKS_TIP_PATH = MAIN_PATH / "lack_blocks_tip"
TEMPERATURE_SLIDER_PATH = MAIN_PATH / "slider"
MAX_VOLUME_BAR_PATH = MAIN_PATH / "pool/max_volume_bar"
VOLUME_SLIDER_PATH = MAIN_PATH / "volume_slider"
MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH = MAIN_PATH / "multi_block_structure_check_btn"


@RegistToolDeltaScreen("FermenterUI.main", is_proxy=True)
class FermenterUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.output_gas_display = self.GetElement(OUT_GAS_DISP_PATH)
        self.output_fluid_display = self.GetElement(OUT_FLUID_DISP_PATH)
        self.pool_img = self.GetElement(POOL_IMG_PATH).asImage()
        self.temperature_label = self.GetElement(TEMPERATURE_LABEL_PATH).asLabel()
        self.expected_temperature_label = self.GetElement(
            EXPECTED_TEMPERATURE_LABEL_PATH
        ).asLabel()
        self.pool_tip = self.GetElement(POOL_TIP_LABEL_PATH).asLabel()
        self.lack_blocks_tip = self.GetElement(LACK_BLOCKS_TIP_PATH).asLabel()
        self.temperature_slider = self.GetElement(TEMPERATURE_SLIDER_PATH).asSlider()
        self.volume_slider = self.GetElement(VOLUME_SLIDER_PATH).asSlider()
        self.volume_bar = self.GetElement(MAX_VOLUME_BAR_PATH).asImage()
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        self.output_gas_displayer = FluidDisplayer(self.output_gas_display)
        self.output_fluid_displayer = FluidDisplayer(self.output_fluid_display)

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        mud_temperature = GetValue(data, K_TEMPERATURE, 0.0)
        mud_thickness = GetValue(data, K_MUD_THICKNESS, 0.0)
        total_volume_pc = GetValue(data, K_TOTAL_VOLUME, 0.0)
        expected_mud_temperature = GetValue(data, K_EXPECTED_TEMPERTURE, 0.0)
        expected_water_max_volume = GetValue(data, K_EXPECTED_WATER_MAX_VOLUME, 0.0)
        structure_destroy_flag = GetValue(data, K_DESTROY_FLAG, 0)
        structure_lacked_blocks = GetStructureLackedBlocks(data)
        structure_lacked_poses = GetStructureLackedBlockPoses(data)
        recipe_id = GetValue(data, K_RECIPE, 0)
        gas_id = GetValue(data, K_OUTPUT_GAS_ID, None)
        gas_volume = GetValue(data, K_OUTPUT_GAS_VOLUME, 0.0)
        gas_max_volume = GetValue(data, K_OUTPUT_GAS_MAX_VOLUME, 0.0)
        fluid_id = GetValue(data, K_OUTPUT_FLUID_ID, None)
        fluid_volume = GetValue(data, K_OUTPUT_FLUID_VOLUME, 0.0)
        fluid_max_volume = GetValue(data, K_OUTPUT_FLUID_MAX_VOLUME, 0.0)
        gas_produce_speed = GetValue(data, K_GAS_PRODUCE_SPEED, 0.0)
        fluid_produce_speed = GetValue(data, K_FLUID_PRODUCE_SPEED, 0.0)
        # self.out_gas_updat_updater()
        # self.out_fluid_updat_updater()
        self.output_gas_displayer.update(gas_id, gas_volume, gas_max_volume)
        self.output_fluid_displayer.update(fluid_id, fluid_volume, fluid_max_volume)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        recipe = spec_recipes.get(recipe_id)
        if recipe is None:
            r, g, b = (
                0,
                0xA6,
                0xFF,
            )
        else:
            color = recipe.color
            r, g, b = (color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF)
        UpdateImageTransformColor(
            self.pool_img,
            0,
            0xA6,
            0xFF,
            r,
            g,
            b,
            mud_thickness,
        )
        self.temperature_slider.SetSliderValue(
            (expected_mud_temperature - TEMPERATURE_MIN)
            / (TEMPERATURE_MAX - TEMPERATURE_MIN)
        )
        self.temperature_label.SetText("酵温 %.1f°C" % mud_temperature)
        self.expected_temperature_label.SetText(
            "控温 %.1f°C" % expected_mud_temperature
        )
        self.volume_bar.SetFullPos(
            "y",
            UICtrlPosData(
                "parent",
                relative_value=0.5 - expected_water_max_volume / POOL_MAX_VOLUME,
            ),
        )
        self.volume_slider.SetSliderValue(
            1 - expected_water_max_volume / POOL_MAX_VOLUME
        )
        self.pool_img.SetFullSize(
            "y", UICtrlPosData("parent", relative_value=total_volume_pc)
        )
        sstatus = structure_destroy_flag
        if sstatus == FLAG_OK:
            self.pool_tip.SetText("发酵池 （就绪）")
        elif sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            self.pool_tip.SetText("发酵池 （缺少必要模块）")
        else:
            self.pool_tip.SetText("发酵池 （结构不完整）")
        if sstatus == DEACTIVE_FLAG_STRUCTURE_BROKEN and structure_lacked_poses:
            fmt = "§l§4结构缺失：\n" + FormatStructureLackedBlockPoses(
                structure_lacked_poses
            )
            self.lack_blocks_tip.SetText(fmt)
        elif structure_lacked_blocks and sstatus == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK:
            fmt = "§l§4结构缺失必须组件：\n" + "\n".join(
                "§9"
                + GetItemHoverName(k).replace("§r", "").replace("§f", "")
                + " x"
                + str(v)
                for k, v in structure_lacked_blocks.items()
            )
            self.lack_blocks_tip.SetText(fmt)
        else:
            if recipe_id == 0:
                fmt = "§l§0无配方"
            else:
                recipe = spec_recipes[recipe_id]
                fmt = (
                    # "§0§3发酵液量： §0%smB" % mud_thickness
                    # + "\n"
                    "§3菌群浓度： §0%.1f%%%%" % (mud_thickness * 100)
                    + "\n"
                    + "§2将产出： §5%s§0、 §3%s"
                    % (
                        GetItemHoverName(recipe.out_gas_id),
                        GetItemHoverName(recipe.out_fluid_id),
                    )
                    + "\n"
                    + (
                        "§4未达到最低产出浓度"
                        if mud_thickness < recipe.produce_thickness
                        else "§2生产中： %.1fmB/s； %.1fmB/s"
                        % (
                            gas_produce_speed,
                            fluid_produce_speed,
                        )
                    )
                )
            self.lack_blocks_tip.SetText(fmt)

    def onCheckMultiBlockStructure(self, _):
        _, x, y, z = self.pos
        MultiBlockStructureCheckRequest(x, y, z).send()
        ExecLater(0.1, self.RemoveUI)

    @Binder.binding(
        Binder.BF_SliderFinished | Binder.BF_SliderFinished,
        "#fermenter.temperature_set_ok",
    )
    def onTemperatureSliderFinished(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        temp = TEMPERATURE_MIN + (TEMPERATURE_MAX - TEMPERATURE_MIN) * progress
        self.expected_temperature_label.SetText("控温 %.1f°C" % temp)
        if finished:
            FermenterSetTemperatureEvent(x, y, z, temp).send()

    @Binder.binding(
        Binder.BF_SliderChanged | Binder.BF_SliderFinished, "#fermenter.volume_setter"
    )
    def onTemperatureSliderChanged(self, progress, finished, _):
        # type: (float, bool, int) -> None
        _, x, y, z = self.pos
        vol = (1 - progress) * POOL_MAX_VOLUME
        if finished:
            FermenterSeMaxVolumeEvent(x, y, z, vol).send()
