# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from ....common.define import flags
from ....common.machinery_def import large_reaction_pool as definition
from ....common.machinery_def.basic import (
    FluidSlotClient, K_DESTROY_FLAG, K_HEAT_VALUE, K_PROGRESS, K_STORE_RF,
)
from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import (
    FluidDisplayer, FormatKelvin, FormatStructureLackedBlockPoses, GetStructureLackedBlockPoses,
    SetHoverText, UpdatePowerBar, UpdateProgress,
)


@RegistToolDeltaScreen("LargeReactionPoolUI.main", is_proxy=True)
class LargeReactionPoolUI(MachinePanelUIProxy):
    STATUS_RINGS = {flags.DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_")}

    def OnCreate(self):
        self.meter = self.GetElement(MAIN_PATH / "power_bar")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        self.temperature = self.GetElement(MAIN_PATH / "temperature")
        self.batch = self.GetElement(MAIN_PATH / "batch_label")
        self.structure = self.GetElement(MAIN_PATH / "structure_not_finished_tip")
        self.detail = self.GetElement(MAIN_PATH / "structure_not_finished_tip/desc_label").asLabel()
        self.structure_state = None
        self.tanks = dict((slot, FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot))))
                          for slot in definition.FLUID_SLOT_MAX_VOLUMES)
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), definition.recipes)

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if not block or not block.get("exData"):
            return
        data = block["exData"]
        progress = GetValue(data, K_PROGRESS, 0)
        UpdateProgress(self.progress, progress)
        UpdatePowerBar(self.meter, GetValue(data, K_STORE_RF, 0), definition.STORE_RF_MAX)
        for slot, tank in self.tanks.items():
            fluid = FluidSlotClient(data, slot)
            tank.update(fluid.fluid_id, fluid.volume, definition.FLUID_SLOT_MAX_VOLUMES[slot])
        recipe = definition.RECIPES_BY_ID.get(GetValue(data, definition.K_RECIPE_ID, ""))
        self.temperature.asLabel().SetText(FormatKelvin(GetValue(data, K_HEAT_VALUE, 300)))
        self.batch.asLabel().SetText("%s\n额定 %d RF/t · %d%%%%" % (
            recipe.title, recipe.power_cost, progress * 100) if recipe else "待机")
        SetHoverText(self.batch, "\n".join(recipe.conditions()) if recipe else "等待完整原料")
        SetHoverText(self.temperature, "\n".join(recipe.conditions()[2:]) if recipe and recipe.heat_cost else "池体温度")
        broken = GetValue(data, K_DESTROY_FLAG, flags.DEACTIVE_FLAG_STRUCTURE_BROKEN)
        state = (broken, GetStructureLackedBlockPoses(data))
        if state != self.structure_state:
            self.structure_state = state
            self.structure.SetVisible(bool(broken))
            if broken:
                self.detail.SetText(FormatStructureLackedBlockPoses(state[1]) if state[1] else "多方块结构未完成")
