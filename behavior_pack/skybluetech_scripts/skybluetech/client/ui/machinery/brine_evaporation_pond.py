# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
    K_DESTROY_FLAG,
    K_HEAT_VALUE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    INPUT_MAX_VOLUME,
    MAX_DISPLAY_TEMPERATURE,
    MIN_DISPLAY_TEMPERATURE,
    OUTPUT_MAX_VOLUME,
    recipes,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import AsRecipeCheckerBtn
from skybluetech_scripts.skybluetech.client.ui.machinery.define import (
    MAIN_PATH,
    MachinePanelUIProxy,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import (
    FluidDisplayer,
    FormatBlockName,
    FormatKelvin,
    FormatStructureLackedBlockPoses,
    GetStructureLackedBlockPoses,
    GetStructureLackedBlocks,
    SetHoverText,
    UpdateProgress,
)

INPUT_FLUID_PATH = MAIN_PATH / "input_fluid_disp"
OUTPUT_FLUID_PATH = MAIN_PATH / "output_fluid_disp"
# 温度计 = SkybluePanelLib.gauge_v (通用计量条, 自下而上), 由 UpdateProgress 驱动, 温度数值在悬停提示;
# 输入 / 输出液量只在流体槽的悬停提示里 (原右侧液量文字板已去掉)
TEMPERATURE_PATH = MAIN_PATH / "temperature"
STRUCTURE_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"


@RegistToolDeltaScreen("BrineEvaporationPondUI.main", is_proxy=True)
class BrineEvaporationPondUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.input_fluid_displayer = FluidDisplayer(self.GetElement(INPUT_FLUID_PATH))
        self.output_fluid_displayer = FluidDisplayer(self.GetElement(OUTPUT_FLUID_PATH))
        self.temperature = self.GetElement(TEMPERATURE_PATH)
        self.last_temperature_ratio = None
        self.structure_tip = self.GetElement(STRUCTURE_TIP_PATH)
        self.structure_desc_label = self.GetElement(
            STRUCTURE_TIP_PATH / "desc_label"
        ).asLabel()
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(tuple(self.pos[1:]))
        if block_data is None:
            return
        data = block_data.get("exData")
        if data is None:
            return
        # 控制器同步接口的只读快照: 下槽为输入口, 上槽为输出口。
        input_fluid = FluidSlotClient(data, 0)
        output_fluid = FluidSlotClient(data, 1)
        self.input_fluid_displayer.update(
            input_fluid.fluid_id, input_fluid.volume, INPUT_MAX_VOLUME
        )
        self.output_fluid_displayer.update(
            output_fluid.fluid_id, output_fluid.volume, OUTPUT_MAX_VOLUME
        )
        current_temperature = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT)
        )
        SetHoverText(
            self.temperature,
            "温度 %s\n§7刻度 %d - %d K"
            % (
                FormatKelvin(current_temperature),
                MIN_DISPLAY_TEMPERATURE,
                MAX_DISPLAY_TEMPERATURE,
            ),
        )
        temperature_ratio = max(
            0.0,
            min(
                1.0,
                (current_temperature - MIN_DISPLAY_TEMPERATURE)
                / (MAX_DISPLAY_TEMPERATURE - MIN_DISPLAY_TEMPERATURE),
            ),
        )
        if temperature_ratio != self.last_temperature_ratio:
            UpdateProgress(self.temperature, temperature_ratio)
            self.last_temperature_ratio = temperature_ratio

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
