# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.ui_pointer import ShowTip
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.events.machinery.seawater_pump import SeawaterPumpModeRequest
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
    K_DESTROY_FLAG,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.seawater_pump import (
    FULL_SPEED_WATER_RATIO,
    K_OUTPUT_MODE,
    K_WATER_BLOCK_COUNT,
    MAX_FLUID_VOLUME,
    MIN_WATER_RATIO,
    MODE_DILUTE_BRINE,
    MODE_RAW_SEAWATER,
    STORE_RF_MAX,
    WATER_SCAN_VOLUME,
    get_output_mode,
)
from skybluetech_scripts.skybluetech.client.ui.machinery_extra_pages import (
    FluidPipeSettingsPage,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.define_ex import (
    MAIN_PATH,
    MachinePanelUIProxyEx,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import (
    FluidDisplayer,
    FormatBlockName,
    FormatStructureLackedBlockPoses,
    GetStructureLackedBlockPoses,
    GetStructureLackedBlocks,
    SetHoverText,
    UpdatePowerBar,
    UpdateProgress,
)

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"
# 水源占比条 = SkybluePanelLib.gauge_h (通用计量条, 30% / 60% 两道刻度在 JSON 里), 由 UpdateProgress 驱动
WATER_RATIO_PATH = MAIN_PATH / "salt_thickness_bar"
STRUCTURE_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"
MODE_DEFAULT_TEXTURE = "textures/ui/skybluetech/button_default"
MODE_SELECTED_TEXTURE = "textures/ui/skybluetech/button_pressed"


@RegistToolDeltaScreen("SeawaterPumpUI.main", is_proxy=True)
class SeawaterPumpUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))
        self.output_mode = None
        self.output_empty = False
        self.mode_buttons = {
            MODE_DILUTE_BRINE: self.GetElement(MAIN_PATH / "mode_brine").asButton(),
            MODE_RAW_SEAWATER: self.GetElement(MAIN_PATH / "mode_raw").asButton(),
        }
        for mode, button in self.mode_buttons.items():
            button.SetCallback(lambda _, mode=mode: self.change_output_mode(mode))
        self.water_ratio_bar = self.GetElement(WATER_RATIO_PATH)
        self.last_water_ratio = None
        self.structure_tip = self.GetElement(STRUCTURE_TIP_PATH)
        self.structure_desc_label = self.GetElement(
            STRUCTURE_TIP_PATH / "desc_label"
        ).asLabel()
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None

    def change_output_mode(self, mode):
        if self.output_mode is None or mode == self.output_mode:
            return
        if not self.output_empty:
            ShowTip("请先停止供电并排空海水泵的输出槽")
            return
        _, x, y, z = self.pos
        SeawaterPumpModeRequest(x, y, z, mode).send()

    def OnTicking(self):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block_data is None:
            return
        data = block_data.get("exData")
        if data is None:
            return
        fluid = FluidSlotClient(data, 0)
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
        self.output_empty = fluid.volume <= 0
        mode = get_output_mode(GetValue(data, K_OUTPUT_MODE, MODE_DILUTE_BRINE))
        if mode != self.output_mode:
            self.output_mode = mode
            for mode_id, button in self.mode_buttons.items():
                button["default"].asImage().SetSprite(
                    MODE_SELECTED_TEXTURE if mode_id == mode else MODE_DEFAULT_TEXTURE
                )

        water_count = GetValue(data, K_WATER_BLOCK_COUNT, 0) or 0
        water_ratio = max(0.0, min(1.0, float(water_count) / WATER_SCAN_VOLUME))
        if water_ratio != self.last_water_ratio:
            UpdateProgress(self.water_ratio_bar, water_ratio)
            SetHoverText(
                self.water_ratio_bar,
                "盐水浓度 %d%%\n§7≥ %d%% 开始抽取, ≥ %d%% 全速"
                % (
                    int(water_ratio * 100),
                    int(MIN_WATER_RATIO * 100),
                    int(FULL_SPEED_WATER_RATIO * 100),
                ),
            )
            self.last_water_ratio = water_ratio

        destroy_flag = GetValue(data, K_DESTROY_FLAG, DEACTIVE_FLAG_STRUCTURE_BROKEN)
        lacked_blocks = GetStructureLackedBlocks(data)
        lacked_poses = GetStructureLackedBlockPoses(data)
        if (
            destroy_flag == self.last_destroy_flag
            and lacked_blocks == self.last_structure_lacked_blocks
            and lacked_poses == self.last_structure_lacked_poses
        ):
            return
        self.last_destroy_flag = destroy_flag
        self.last_structure_lacked_blocks = dict(lacked_blocks)
        self.last_structure_lacked_poses = lacked_poses
        self.structure_tip.SetVisible(destroy_flag != 0)
        if destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN and lacked_poses:
            text = FormatStructureLackedBlockPoses(lacked_poses)
        elif destroy_flag == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK and lacked_blocks:
            text = "缺失组件： " + "， ".join(
                "%sx%d" % (FormatBlockName(block_id), count)
                for block_id, count in sorted(lacked_blocks.items())
            )
        else:
            text = "多方块结构未完成"
        self.structure_desc_label.SetText(text)


