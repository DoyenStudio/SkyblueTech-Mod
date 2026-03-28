# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ....common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from ....common.ui_sync.machinery.bedrock_lava_drill import BedrockLavaDrillUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, InitFluidDisplay

POWER_NODE = MAIN_PATH / "power_bar"
FLUID_NODE = MAIN_PATH / "fluid_display"
DRILL_PROGRESS_NODE = MAIN_PATH / "drill_progress/progress_bar/bar_mask"
STORAGE_LEFT_NODE = MAIN_PATH / "storage_left/progress_bar/bar_mask"
STRUCTURE_NOT_FINISHED_TIP_NODE = MAIN_PATH / "structure_not_finished_tip"
STRUCTURE_DESC_LABEL_NODE = STRUCTURE_NOT_FINISHED_TIP_NODE / "desc_label"
MULTIBLOCK_STRUCTURE_CHECK_BTN_NODE = MAIN_PATH / "multi_block_structure_check_btn"


@RegistToolDeltaScreen("BedrockLavaDrillUI.main", is_proxy=True)
class BedrockLavaDrillUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.power_bar = self.GetElement(POWER_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.drill_progress = self.GetElement(DRILL_PROGRESS_NODE)
        self.storage_left = self.GetElement(STORAGE_LEFT_NODE)
        self.structure_not_finished_tip = self.GetElement(
            STRUCTURE_NOT_FINISHED_TIP_NODE
        )
        self.structure_desc_label = self.GetElement(STRUCTURE_DESC_LABEL_NODE).asLabel()
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_NODE)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        self.fluid_updater = InitFluidDisplay(
            self.fluid_display,
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            ),
        )
        self._last_structure_flag = None
        self.sync = BedrockLavaDrillUISync.NewClient(dim, x, y, z)  # type: BedrockLavaDrillUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.fluid_updater()
        self.drill_progress.SetFullSize(
            "x", UICtrlPosData("parent", self.sync.drill_progress)
        )
        self.storage_left.SetFullSize(
            "x", UICtrlPosData("parent", self.sync.lava_storage_left)
        )
        if self.sync.structure_flag != self._last_structure_flag:
            self.structure_not_finished_tip.SetVisible(self.sync.structure_flag != 0)
            self._last_structure_flag = self.sync.structure_flag
            if self.sync.structure_lacked_blocks:
                self.structure_desc_label.SetText(
                    "缺失组件： "
                    + "， ".join(
                        GetItemHoverName(b) + "x" + str(n)
                        for b, n in self.sync.structure_lacked_blocks.items()
                    )
                )
            else:
                self.structure_desc_label.SetText("多方块结构未完成")

    def onCheckMultiBlockStructure(self, _):
        _, x, y, z = self.pos
        MultiBlockStructureCheckRequest(x, y, z).send()
