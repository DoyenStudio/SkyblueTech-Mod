# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from ....common.define import flags
from ....common.machinery_def import gas_metallurgical_furnace as definition
from ....common.machinery_def.basic import K_PROGRESS, K_STORE_RF, K_DESTROY_FLAG, FluidSlotClient
from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import (
    FluidDisplayer, UpdatePowerBar, UpdateProgress, SetHoverText,
    GetStructureLackedBlockPoses, FormatStructureLackedBlockPoses, GetStructureLackedBlocks,
)


@RegistToolDeltaScreen("GasMetallurgicalFurnaceUI.main", is_proxy=True)
class GasMetallurgicalFurnaceUI(MachinePanelUIProxy):
    STATUS_RINGS = {flags.DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_")}

    def OnCreate(self):
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        self.batch_tip = self.GetElement(MAIN_PATH / "batch_label")
        self.batch_label = self.GetElement(MAIN_PATH / "batch_label").asLabel()
        self.structure_not_finished_tip = self.GetElement(MAIN_PATH / "structure_not_finished_tip")
        self.structure_desc_label = self.GetElement(MAIN_PATH / "structure_not_finished_tip/desc_label").asLabel()
        self.last_structure_state = None
        self.tanks = dict((slot, FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot))))
                          for slot in definition.FLUID_SLOT_MAX_VOLUMES)
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), definition.recipes)

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        progress = GetValue(data, K_PROGRESS, 0.0)
        UpdateProgress(self.progress, progress)
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), definition.STORE_RF_MAX)
        for slot, display in self.tanks.items():
            fluid = FluidSlotClient(data, slot)
            display.update(fluid.fluid_id, fluid.volume, definition.FLUID_SLOT_MAX_VOLUMES[slot])
        recipe = definition.RECIPES_BY_ID.get(GetValue(data, definition.K_RECIPE_ID, ""))
        if recipe is None:
            self.batch_label.SetText("待机")
            SetHoverText(self.batch_tip, "等待完整原料")
        else:
            self.batch_label.SetText("%d RF/t  ·  %d%%" % (recipe.power_cost, progress * 100))
            SetHoverText(self.batch_tip, "%s\n整批耗电 %d RF\n剩余 %.1f s" % (
                recipe.title, recipe.total_rf, max(0, 1 - progress) * recipe.tick_duration / 20.0))
        self._update_structure_tip(data)

    def _update_structure_tip(self, data):
        ready = GetValue(data, definition.K_TEMPLATE_READY, False)
        destroy_flag = GetValue(data, K_DESTROY_FLAG, flags.DEACTIVE_FLAG_STRUCTURE_BROKEN)
        lacked_blocks = GetStructureLackedBlocks(data)
        lacked_poses = GetStructureLackedBlockPoses(data)
        state = (ready, destroy_flag, lacked_blocks, lacked_poses)
        if state != self.last_structure_state:
            self.last_structure_state = state
            self.structure_not_finished_tip.SetVisible(not ready or destroy_flag != 0)
            if not ready:
                detail = "结构模板待配置"
            elif destroy_flag == flags.DEACTIVE_FLAG_STRUCTURE_BROKEN and lacked_poses:
                detail = FormatStructureLackedBlockPoses(lacked_poses)
            elif destroy_flag == flags.DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK and lacked_blocks:
                detail = "缺失组件： " + "， ".join(
                    (CF.CreateItem(LEVEL_ID).GetItemHoverName(block_id) or block_id) + "x" + str(count)
                    for block_id, count in lacked_blocks.items()
                )
            else:
                detail = "多方块结构未完成"
            self.structure_desc_label.SetText(detail)
