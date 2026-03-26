# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.mini_jei.core.define import CategoryType
from ....common.mini_jei.machinery.recipe_cls import MachineRecipe
from .base_machine import BaseMachine
from .base_processor import BaseProcessor
from .upgrade_control import UpgradeControl
from .multi_fluid_container import MultiFluidContainer, FluidSlot


class MixedProcessor(BaseProcessor, MultiFluidContainer):
    """
    能使用物品和流体的配方处理器机器基类。

    派生自:
        `BaseProcessor`
        `MultiFluidContainer`
    """

    @SuperExecutorMeta.execute_super_with_blacklist(BaseProcessor)
    def __init__(self, dim, x, y, z, block_entity_data):
        self.current_recipe = self.get_recipe(self.GetInputSlotItems(), self.fluids)
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        self.afterRequireAll()

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnTryActivate(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            return
        if slot_pos in self.output_slots and self.HasDeactiveFlag(
            flags.DEACTIVE_FLAG_OUTPUT_FULL
        ):
            self.start_next()
            return
        elif slot_pos in self.input_slots:
            recipe = self.get_recipe(self.GetInputSlotItems(), self.fluids)
            if recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                self.current_recipe = None
                self.ResetProgress()
            elif not recipe.equals(self.current_recipe):
                self.start_next()

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if not is_final:
            return
        if slot in self.fluid_output_slots:
            if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                self.start_next()
                return
        elif slot in self.fluid_input_slots:
            if not self.IsActive():
                return
            recipe = self.get_recipe(self.GetInputSlotItems(), self.fluids)
            if recipe is None:
                if self.current_recipe is not None:
                    self.current_recipe = None
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                    self.ResetProgress()
            elif not recipe.equals(self.current_recipe):
                self.start_next()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        for recipe in self.recipes:
            slot_input = recipe.inputs.get("fluid", {}).get(slot)
            if slot_input is None:
                continue
            if slot_input.match_item_id(fluid_id):
                return True
        return False

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if not is_final:
            return
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE):
            if self.current_recipe is None:
                self.start_next()
            else:
                # fix here
                print("[Warning] MixedProcessor: Recipe ERROR")
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    @Delay(1)
    def afterRequireAll(self):
        self.RequireItems()
        self.RequireFluidsFromNetwork()
        self.OnSync()

    def start_next(self, dont_recursive=False):
        self.RequireItems()
        self.RequireFluidsFromNetwork()
        input_slots = self.GetInputSlotItems()
        output_slots = self.GetOutputSlotItems()
        fluids = self.fluids
        recipe = self.get_recipe(input_slots, fluids)
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
            return
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        self.SetPower(recipe.power_cost)
        self.ResetProgress()
        if not self.can_output(recipe, output_slots):
            # 输出堵塞
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        if not self.PowerEnough():
            return
        self.ResetDeactiveFlags()
        self.CallSync()

    def run_once(self):
        "进行一次配方产出"
        input_items = self.GetInputSlotItems()
        output_items = self.GetOutputSlotItems()
        self.current_recipe = self.get_recipe(input_items, self.fluids)
        if self.current_recipe is None:
            # cannot reach
            raise ValueError("Recipe ERROR")
        if not self.can_output(self.current_recipe, output_items):
            return
        input_items.update(output_items)
        self.finish_recipe(input_items, self.current_recipe)
        self.RequireAnyFluidFromNetwork()

    def get_recipe(self, input_items, input_fluids):
        # type: (dict[int, Item], list[FluidSlot]) -> MachineRecipe | None
        for recipe in self.recipes:
            cont = False
            for slot_pos, input in recipe.inputs.get(CategoryType.ITEM, {}).items():
                item = input_items.get(slot_pos, None)
                if item is None:
                    cont = True
                    break
                if not input.match_item_id(item.id) or item.count < input.count:
                    cont = True
                    break
            for slot_pos, input in recipe.inputs.get(CategoryType.FLUID, {}).items():
                fluid = input_fluids[slot_pos]
                if fluid.fluid_id is None:
                    cont = True
                    break
                if (
                    not input.match_item_id(fluid.fluid_id)
                    or fluid.volume < input.count
                ):
                    cont = True
                    break
            if cont:
                continue
            else:
                return recipe
        return None

    def can_output(self, recipe, output_item_slots):
        # type: (MachineRecipe, dict[int, Item]) -> bool
        outputs = recipe.outputs
        for slot_pos, output in outputs.get(CategoryType.ITEM, {}).items():
            item = output_item_slots.get(slot_pos, None)
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
        for slot_pos, output in outputs.get(CategoryType.FLUID, {}).items():
            fluid = self.fluids[slot_pos]
            if fluid.fluid_id is None:
                # TODO: 假设输出不可能超过流体槽最大容量
                fluid_volume = output.count
                continue
            elif fluid.fluid_id != output.id:
                return False
            else:
                fluid_volume = fluid.volume + output.count
            if fluid_volume > fluid.max_volume:
                return False
        return True

    def finish_recipe(self, slotitems, recipe):
        # type: (dict[int, Item], MachineRecipe) -> None
        fluid_slots = self.fluids
        for slot_pos, input in recipe.inputs.get(CategoryType.ITEM, {}).items():
            slotitems[slot_pos].count -= int(input.count)
        for slot_pos, input in recipe.inputs.get(CategoryType.FLUID, {}).items():
            fluid_slots[slot_pos].volume -= input.count
        for slot_pos, output in recipe.outputs.get(CategoryType.ITEM, {}).items():
            orig_item = slotitems.get(slot_pos, None)
            if orig_item is None:
                orig_item = Item(output.id, 0, int(output.count))
            else:
                orig_item.count += int(output.count)
            slotitems[slot_pos] = orig_item
        slots_and_outputs = list(recipe.outputs.get(CategoryType.FLUID, {}).items())
        if slots_and_outputs:
            last_slot_pos = slots_and_outputs[-1][0]
            for slot_pos, output in slots_and_outputs:
                self.OutputFluid(
                    output.id, output.count, slot_pos, slot_pos == last_slot_pos
                )
        self.SetSlotItems(slotitems)
