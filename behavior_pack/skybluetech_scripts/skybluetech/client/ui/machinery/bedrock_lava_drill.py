# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_DESTROY_FLAG,
)
from skybluetech_scripts.skybluetech.common.machinery_def.bedrock_lava_drill import (
    STORE_RF_MAX,
    K_DRILL_PROGRESS,
    K_VOLUME_LEFT_PERCENT,
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_FLUID_VOLUME,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import (
    UpdatePowerBar,
    FluidDisplayer,
    GetStructureLackedBlocks,
    GetStructureLackedBlockPoses,
    FormatStructureLackedBlockPoses,
)

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"
DRILL_PROGRESS_PATH = MAIN_PATH / "drill_progress/progress_bar/bar_mask"
STORAGE_LEFT_PATH = MAIN_PATH / "storage_left/progress_bar/bar_mask"
STRUCTURE_NOT_FINISHED_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"
STRUCTURE_DESC_LABEL_PATH = STRUCTURE_NOT_FINISHED_TIP_PATH / "desc_label"
MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH = MAIN_PATH / "multi_block_structure_check_btn"


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
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        self.fluid_displayer = FluidDisplayer(
            self.fluid_display,
        )
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
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
        self.drill_progress.SetFullSize("x", UICtrlPosData("parent", drill_progress))
        self.storage_left.SetFullSize("x", UICtrlPosData("parent", lava_storage_left))
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
                        GetItemHoverName(b) + "x" + str(n)
                        for b, n in structure_lacked_blocks.items()
                    )
                )
            else:
                self.structure_desc_label.SetText("多方块结构未完成")

    def onCheckMultiBlockStructure(self, _):
        _, x, y, z = self.pos
        MultiBlockStructureCheckRequest(x, y, z).send()
