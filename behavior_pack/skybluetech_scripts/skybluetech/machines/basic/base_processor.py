# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from ...define.machine_config import MachineRecipe
from ...define import flags as flags
from .auto_saver import AutoSaver
from .base_machine import BaseMachine
from .gui_ctrl import GUIControl
from .sp_control import SPControl
from .upgrade_control import UpgradeControl
from .work_renderer import WorkRenderer


# TODO: 两个机器都 deactive 的情况

class BaseProcessor(AutoSaver, GUIControl, UpgradeControl, WorkRenderer):
    """
    基本的配方处理器机器基类。
    只运行简单物品配方的机器均可继承此类。
    """
    recipes = [] # type: list[MachineRecipe]
    "机器配方, 改变配方表时记得重置工作进度"
    # output_slot_index = 0
    # "允许漏斗漏出的槽位"
    energy_mode = (0, 0, 0, 0, 0, 0)
    

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.current_recipe = None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        SPControl.OnLoad(self)
        self.current_recipe = self.getRecipe(self.GetInputSlotItems())
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def OnTicking(self):
        while self.IsActive():
            if self.current_recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                return
            do_break = False
            if self.ProcessOnce():
                # 1tick 内有可能需要多次生产
                self.runOnce()
                self.Dump()
                self.StartNext()
            else:
                do_break = True
            self.OnSync()
            if do_break:
                break

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            UpgradeControl.OnSlotUpdate(self, slot_pos)
            return
        if slot_pos in self.output_slots:
            if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                # i dont sure
                if (
                    self.current_recipe is not None
                    and self.canOutput(self.current_recipe, self.GetOutputSlotItems())
                ):
                    self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            else:
                return
        recipe = self.getRecipe(self.GetInputSlotItems())
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
        elif not recipe.equals(self.current_recipe):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.StartNext()
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def OnTryActivate(self):
        self.ResetDeactiveFlags() # TODO: 安全问题?

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)

    # ==== process ====

    def runOnce(self):
        "进行一次配方产出"
        inputs = self.GetInputSlotItems()
        outputs = self.GetOutputSlotItems()
        recipe = self.getRecipe(inputs)
        if recipe is None:
            # cannot reach
            raise ValueError("Recipe ERROR")
        if not self.canOutput(recipe, outputs):
            return
        inputs.update(outputs)
        self.finishRecipeOnce(inputs, recipe)

    def StartNext(self, dont_recursive=False):
        "开始运行配方"
        input_slots = self.GetInputSlotItems()
        output_slots = self.GetOutputSlotItems()
        recipe = self.getRecipe(input_slots)
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            if not dont_recursive:
                # 可能是物品不够了, 尝试向附近的管道网络索取物品
                ok = self.RequireItems()
                if ok:
                    self.StartNext(dont_recursive=True)
            return
        elif not self.canOutput(recipe, output_slots):
            # 输出堵塞
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        self.current_recipe = recipe
        self.SetPower(recipe.power_cost)
        if not self.PowerEnough():
            return
        self.SetProcessTicks(recipe.tick_duration)
        self.ResetProgress()
        self.ResetDeactiveFlags()
        self.OnSync()

    # ==== utils ====

    def GetProgressPercent(self):
        r = self.current_recipe
        if r is None:
            return 0
        return 1 - float(self.ticks_left) / r.tick_duration

    # ==== self utils ====

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot in self.output_slots:
            return False
        elif self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        for recipe in self.recipes:
            slot_input = recipe.inputs.get("item", {}).get(slot)
            if slot_input is None:
                continue
            if slot_input.is_tag:
                if slot_input.id in item.GetBasicInfo().tags:
                    return True
            else:
                if slot_input.id == item.newItemName:
                    return True
        return False

    def getRecipe(self, inputs):
        # type: (dict[int, Item]) -> MachineRecipe | None
        for recipe in self.recipes:
            cont = False
            for slot_pos, input in recipe.inputs.get("item", {}).items():
                item = inputs.get(slot_pos, None)
                if item is None:
                    cont = True
                    break
                if (
                    input.id not in item.GetBasicInfo().tags
                    if input.is_tag else input.id != item.newItemName
                ) or item.count < input.count:
                    cont = True
                    break
            if cont:
                continue
            else:
                return recipe
        return None

    def canRunRecipe(self):
        if self.current_recipe is None:
            return False
        return self.store_rf >= self.current_recipe.power_cost

    @staticmethod
    def canOutput(recipe, output_slots):
        # type: (MachineRecipe, dict[int, Item]) -> bool
        outputs = recipe.outputs.get("item", {})
        for slot_pos, output in outputs.items():
            item = output_slots.get(slot_pos, None)
            if item is None:
                # TODO: 假设输出不可能超过物品最大堆叠数
                item_count = output.count
                continue
            elif item.newItemName != output.id:
                # TODO: auxValue and nbt comparison
                return False
            else:
                item_count = item.count + output.count
            if item_count > item.GetBasicInfo().maxStackSize:
                return False
        return True

    def finishRecipeOnce(self, slotitems, recipe):
        # type: (dict[int, Item], MachineRecipe) -> None
        for slot_pos, input in recipe.inputs.get("item", {}).items():
            slotitems[slot_pos].count -= int(input.count)
        for slot_pos, output in recipe.outputs.get("item", {}).items():
            orig_item = slotitems.get(slot_pos, None)
            if orig_item is None:
                orig_item = Item(output.id, 0, int(output.count))
            else:
                orig_item.count += int(output.count)
            slotitems[slot_pos] = orig_item
        self.SetSlotItems(slotitems)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BaseMachine.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)
