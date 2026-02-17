# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.item import GetItemBasicInfo
from skybluetech_scripts.tooldelta.api.timer import Delay
from ...define import flags
from ...mini_jei.core.define import CategoryType
from ...mini_jei.machines.recipe_cls import MachineRecipe
from .base_machine import BaseMachine
from .base_processor import BaseProcessor
from .upgrade_control import UpgradeControl
from .multi_fluid_container import MultiFluidContainer, FluidSlot
from .sp_control import SPControl


class MixedProcessor(BaseProcessor, MultiFluidContainer):
    """
    能使用物品和流体的配方处理器机器基类。

    派生自:
        `BaseProcessor`
        `MultiFluidContainer`
    """

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        MultiFluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.current_recipe = self.get_recipe(self.GetInputSlotItems(), self.fluids)
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def OnPlaced(self, _):
        self.afterRequireAll()

    def OnTicking(self):
        BaseProcessor.OnTicking(self)
        MultiFluidContainer.OnTicking(self)

    def OnTryActivate(self):
        BaseMachine.OnTryActivate(self)
        MultiFluidContainer.OnTryActivate(self)

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
            return
        elif not self.can_output(recipe, output_slots):
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

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        for recipe in self.recipes:
            slot_input = recipe.inputs.get("fluid", {}).get(slot)
            if slot_input is None:
                continue
            if slot_input.is_tag:
                if slot_input.id in GetItemBasicInfo(fluid_id).tags:
                    return True
            else:
                if slot_input.id == fluid_id:
                    return True
        return False

    def run_once(self):
        "进行一次配方产出"
        input_items = self.GetInputSlotItems()
        output_items = self.GetOutputSlotItems()
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
                if (
                    input.id not in item.GetBasicInfo().tags
                    if input.is_tag
                    else input.id != item.newItemName
                ) or item.count < input.count:
                    cont = True
                    break
            for slot_pos, input in recipe.inputs.get(CategoryType.FLUID, {}).items():
                fluid = input_fluids[slot_pos]
                if fluid.fluid_id is None:
                    cont = True
                    break
                if (
                    input.id not in Item(fluid.fluid_id).GetBasicInfo().tags
                    if input.is_tag
                    else fluid.fluid_id != input.id
                ) or fluid.volume < input.count:
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

    def OnFluidSlotUpdate(self, slot):
        if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE):
            input_slots = self.GetInputSlotItems()
            fluids = self.fluids
            recipe = self.get_recipe(input_slots, fluids)
            if recipe is not None:
                self.current_recipe = recipe
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

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
        for slot_pos, output in recipe.outputs.get(CategoryType.FLUID, {}).items():
            self.OutputFluid(output.id, output.count, slot_pos)
        self.SetSlotItems(slotitems)

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if self.InUpgradeSlot(slot_pos):
            UpgradeControl.OnSlotUpdate(self, slot_pos)
            return
        if slot_pos in self.output_slots and self.HasDeactiveFlag(
            flags.DEACTIVE_FLAG_OUTPUT_FULL
        ):
            self.start_next()
            return
        recipe = self.get_recipe(self.GetInputSlotItems(), self.fluids)
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
        elif not recipe.equals(self.current_recipe):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.start_next()
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
