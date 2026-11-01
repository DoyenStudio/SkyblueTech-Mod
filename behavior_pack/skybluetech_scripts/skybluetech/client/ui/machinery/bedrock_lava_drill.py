# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_DESTROY_FLAG,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.bedrock_lava_drill import (
    K_DRILL_PROGRESS,
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_FLUID_VOLUME,
    K_VOLUME_LEFT_PERCENT,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import (
    FluidDisplayer,
    FormatStructureLackedBlockPoses,
    GetStructureLackedBlockPoses,
    GetStructureLackedBlocks,
    SetHoverText,
    UpdatePowerBar,
    UpdateProgress,
)

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"
# 两条进度都是 SkybluePanelLib.gauge_h (通用计量条), 由 UpdateProgress 驱动, 百分比写进悬停提示
DRILL_PROGRESS_PATH = MAIN_PATH / "drill_progress"
STORAGE_LEFT_PATH = MAIN_PATH / "storage_left"
STRUCTURE_NOT_FINISHED_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"
STRUCTURE_DESC_LABEL_PATH = STRUCTURE_NOT_FINISHED_TIP_PATH / "desc_label"


@RegistToolDeltaScreen("BedrockLavaDrillUI.main", is_proxy=True)
class BedrockLavaDrillUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.fluid_display = self.GetElement(FLUID_PATH)
        self.drill_progress = self.GetElement(DRILL_PROGRESS_PATH)
        self.storage_left = self.GetElement(STORAGE_LEFT_PATH)
        self.structure_not_finished_tip = self.GetElement(
            STRUCTURE_NOT_FINISHED_TIP_PATH
        )
        self.structure_desc_label = self.GetElement(STRUCTURE_DESC_LABEL_PATH).asLabel()
        self.fluid_displayer = FluidDisplayer(
            self.fluid_display,
        )
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        fluid_id = GetValue(data, K_FLUID_ID, None)
        fluid_volume = GetValue(data, K_FLUID_VOLUME, 0.0)
        max_volume = GetValue(data, K_MAX_FLUID_VOLUME, 1.0)
        drill_progress = GetValue(data, K_DRILL_PROGRESS, 0.0)
        lava_storage_left = GetValue(data, K_VOLUME_LEFT_PERCENT, 0.0)
        destroy_flag = GetValue(data, K_DESTROY_FLAG, 0)
        structure_lacked_blocks = GetStructureLackedBlocks(data)
        structure_lacked_poses = GetStructureLackedBlockPoses(data)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        self.fluid_displayer.update(fluid_id, fluid_volume, max_volume)
        UpdateProgress(self.drill_progress, drill_progress)
        SetHoverText(self.drill_progress, "钻探进度 %d%%" % int(drill_progress * 100))
        UpdateProgress(self.storage_left, lava_storage_left)
        SetHoverText(self.storage_left, "熔岩剩余量 %d%%" % int(lava_storage_left * 100))
        if (
            destroy_flag != self.last_destroy_flag
            or structure_lacked_blocks != self.last_structure_lacked_blocks
            or structure_lacked_poses != self.last_structure_lacked_poses
        ):
            self.structure_not_finished_tip.SetVisible(destroy_flag != 0)
            self.last_destroy_flag = destroy_flag
            self.last_structure_lacked_blocks = dict(structure_lacked_blocks)
            self.last_structure_lacked_poses = structure_lacked_poses
            if (
                destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN
                and structure_lacked_poses
            ):
                self.structure_desc_label.SetText(
                    FormatStructureLackedBlockPoses(structure_lacked_poses)
                )
            elif (
                destroy_flag == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
                and structure_lacked_blocks
            ):
                self.structure_desc_label.SetText(
                    "缺失组件： "
                    + "， ".join(
                        CF.CreateItem(LEVEL_ID).GetItemHoverName(b) + "x" + str(n)
                        for b, n in structure_lacked_blocks.items()
                    )
                )
            else:
                self.structure_desc_label.SetText("多方块结构未完成")
