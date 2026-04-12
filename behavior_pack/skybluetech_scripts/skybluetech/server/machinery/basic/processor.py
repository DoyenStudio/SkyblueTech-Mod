# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.mini_jei.core import CategoryType, RecipesCollection
from ....common.mini_jei.machinery import MachineRecipeBase, MachineRecipe
from ....common.define import flags as flags
from .multi_fluid_container import MultiFluidContainer
from .upgrade_control import UpgradeControl
from .processor_base import ProcessorBase


class Processor(ProcessorBase, UpgradeControl):
    """
    配方处理器机器基类; 继承时需要把 Processor 放在最后以免 __init__ 顺序出问题

    目前支持处理 (记得把对应的 process_xxx 设为 True):
        - 物品
        - 流体
    """

    recipes = RecipesCollection("???")  # type: RecipesCollection[MachineRecipe]
    "机器配方, 改变配方表时记得重置工作进度"
    energy_mode = (0, 0, 0, 0, 0, 0)
    allow_upgrader_tags = {
        "skybluetech:upgraders/speed",
        "skybluetech:upgraders/energy",
    }

    def OnTicking(self):
        while self.IsActive():
            if self.current_recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                return
            if self.ProcessOnce():
                # 1tick 内有可能需要多次生产
                self.run_once()
                self.start_next()
                self.CallSync()
            else:
                self.CallSync()
                break

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def GetProgressPercent(self):
        r = self.current_recipe
        if r is None:
            return 0
        return 1 - float(self.ticks_left) / r.tick_duration

    # === item processor special ===
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            UpgradeControl.OnSlotUpdate(self, slot_pos)
            return
        if self.process_item:
            if slot_pos in self.output_slots and self.HasDeactiveFlag(
                flags.DEACTIVE_FLAG_OUTPUT_FULL
            ):
                self.start_next()
                return
            elif slot_pos in self.input_slots:
                self.recheck_recipe()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot in self.output_slots:
            return False
        for recipe in self.recipes:
            slot_input = recipe.inputs.get(CategoryType.ITEM, {}).get(slot)
            if slot_input is None:
                continue
            if slot_input.match_item_id(item.id):
                return True
        return False

    # === fluid processor special ===
    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if not is_final or not isinstance(self, MultiFluidContainer):
            return
        if slot in self.fluid_output_slots and self.HasDeactiveFlag(
            flags.DEACTIVE_FLAG_NO_RECIPE
        ):
            self.recheck_recipe()

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if not is_final or not isinstance(self, MultiFluidContainer):
            return
        if slot in self.fluid_output_slots:
            if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                self.start_next()
                return
        elif slot in self.fluid_input_slots:
            self.recheck_recipe()

    # ======
    def recheck_recipe(self):
        _, recipe = self.get_recipe()
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
            self.ResetProgress()
        elif not recipe.equals(self.current_recipe):
            self.start_next(recipe)
        elif self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
            self.start_next(recipe)

    def run_once(self):
        "进行一次配方产出"
        _, recipe = self.get_recipe()
        if recipe is None:
            # cannot reach
            raise ValueError("Recipe ERROR")
        if not self.can_output(recipe):
            return
        self.finish_recipe(recipe)

    def start_next(self, _recipe=None):
        # type: (MachineRecipeBase | None) -> None
        "开始运行配方"
        if _recipe is None:
            recipe = self.get_recipe()
            if recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                self.current_recipe = None
                return
        else:
            recipe = _recipe
        if not isinstance(recipe, MachineRecipe):
            raise ValueError(
                "Processor %s run recipe not MachineRecipe" % self.__class__.__name__
            )
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        self.ResetProgress()
        if not self.can_output(recipe):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        self.SetPower(recipe.power_cost)
        if not self.PowerEnough():
            return
        self.ResetDeactiveFlags()
        self.CallSync()

    def finish_recipe(self, recipe):
        # type: (MachineRecipeBase) -> None
        slotitems = self.GetInputSlotItems()
        slotitems.update(self.GetOutputSlotItems())
        if self.process_item:
            for slot_pos, input in recipe.inputs.get(CategoryType.ITEM, {}).items():
                slotitems[slot_pos].count -= int(input.count)
            for slot_pos, output in recipe.outputs.get(CategoryType.ITEM, {}).items():
                orig_item = slotitems.get(slot_pos, None)
                if orig_item is None:
                    orig_item = Item(output.id, 0, int(output.count))
                else:
                    orig_item.count += int(output.count)
                slotitems[slot_pos] = orig_item
            self.SetSlotItems(slotitems)
        if self.process_fluid and isinstance(self, MultiFluidContainer):
            slot_pos_and_inputs = list(
                recipe.inputs.get(CategoryType.FLUID, {}).items()
            )
            last_index = len(slot_pos_and_inputs) - 1
            for idx, (slot_pos, input) in enumerate(slot_pos_and_inputs):
                self.fluids[slot_pos].volume -= input.count
                self.onReducedFluid(slot_pos, input.id, input.count, idx == last_index)
            slots_pos_and_outputs = list(
                recipe.outputs.get(CategoryType.FLUID, {}).items()
            )
            last_index = len(slots_pos_and_outputs) - 1
            for idx, (slot_pos, input) in enumerate(slots_pos_and_outputs):
                self.OutputFluid(output.id, output.count, slot_pos, idx == last_index)
