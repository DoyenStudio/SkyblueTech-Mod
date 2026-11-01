# coding=utf-8
import random

from skybluetech_scripts.skybluetech.common.define import flags as flags
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
)
from skybluetech_scripts.skybluetech.common.mini_jei.core import (
    CategoryType,
    RecipesCollection,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import MachineRecipeBase
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.server.machinery.utils.recipe_plan import (
    get_recipe_plan,
)

from .gui_ctrl import GUIControl
from .multi_fluid_container import MultiFluidContainer
from .upgrade_control import UpgradeControl
from .work_renderer import WorkRenderer


class ProcessorBase(WorkRenderer, UpgradeControl, GUIControl):
    """
    配方处理器基类。
    """

    process_item = False
    "是否处理物品; 输入或输出中有物品都要设为 True"
    process_fluid = False
    "是否处理流体; 输入或输出中有流体都要设为 True"

    recipes = RecipesCollection("???")  # type: RecipesCollection[MachineRecipeBase]
    "机器配方, 改变配方表时记得重置工作进度"

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ProcessorBase, self).__init__(dim, x, y, z, block_entity_data)
        self._applying_recipe = False
        _, self.current_recipe = self.get_recipe()
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        else:
            # 停机旗是落盘保存的, 老存档可能带着"无配方"旗存下来(比如输入是后来才补上的),
            # 构造时既然已经匹配到配方, 就顺手把它清掉, 否则机器重进世界后再也醒不过来
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)


    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        results = (
            MultiFluidContainer.IsValidFluidInput(self, slot, fluid_id),
            self._processor_base_is_valid_fluid_input(slot, fluid_id),
        )
        return all(results)

    def _processor_base_is_valid_fluid_input(self, slot, fluid_id):
        # type: (int, str) -> bool
        return self._recipe_accepts_input(CategoryType.FLUID, slot, fluid_id)

    def _recipe_accepts_input(self, category, slot, item_id, aux=0):
        return any(
            get_recipe_plan(recipe).input_matches(category, slot, item_id, aux)
            for recipe in self.recipes
        )

    def update_gui(self):
        if self.current_recipe is not None:
            self.bdata[K_PROGRESS] = self.GetProcessProgress()

    def get_recipe(self):
        # type: () -> tuple[int, MachineRecipeBase | None]
        # 原生容器读取较贵；一轮选方只读取一次，所有候选共用快照。
        items = self.GetInputSlotItems() if self.process_item else {}
        for recipe_idx, recipe in enumerate(self.recipes):
            plan = get_recipe_plan(recipe)
            if self.process_item and plan.plan_item_inputs(items) is None:
                continue
            if self.process_fluid and isinstance(self, MultiFluidContainer):
                if plan.plan_fluid_inputs(self.fluids) is None:
                    continue
            return recipe_idx, recipe
        return (0, None)

    def can_output(self, recipe):
        # type: (MachineRecipeBase) -> bool
        plan = get_recipe_plan(recipe)
        if self.process_item:
            if plan.plan_item_outputs(
                self.GetOutputSlotItems(), self.item_output_slots
            ) is None:
                return False
        if self.process_fluid and isinstance(self, MultiFluidContainer):
            if plan.plan_fluid_outputs(self.fluids, self.fluid_output_slots) is None:
                return False
        return True

    def _apply_recipe(self, recipe, consume_inputs=True, produce_outputs=True):
        "按当前库存重新分配，全部检查成功后才扣料/产出，不缓存库存或随机结果。"
        plan = get_recipe_plan(recipe)
        item_inputs, item_outputs, fluid_inputs, fluid_outputs = [], [], [], []
        items = {}
        if self.process_item:
            if consume_inputs:
                items = self.GetInputSlotItems()
                item_inputs = plan.plan_item_inputs(items)
                if item_inputs is None:
                    return False
            if produce_outputs:
                outputs = self.GetOutputSlotItems()
                item_outputs = plan.plan_item_outputs(outputs, self.item_output_slots)
                if item_outputs is None:
                    return False
                items.update(outputs)
        if self.process_fluid and isinstance(self, MultiFluidContainer):
            if consume_inputs:
                fluid_inputs = plan.plan_fluid_inputs(self.fluids)
                if fluid_inputs is None:
                    return False
            if produce_outputs:
                fluid_outputs = plan.plan_fluid_outputs(self.fluids, self.fluid_output_slots)
                if fluid_outputs is None:
                    return False

        changed_items = {}
        output_slots = set()
        reduced_fluids, added_fluids = {}, {}
        for allocation in item_inputs:
            for slot, count in allocation.items():
                items[slot].count -= int(count)
                changed_items[slot] = items[slot]
        for (_, output), allocation in zip(plan.outputs.get(CategoryType.ITEM, ()), item_outputs):
            if not allocation or (output.prob != 1 and random.random() > output.prob):
                continue
            # 概率属于原始产物条目，拆到多个槽时也只抽一次。
            for slot, count in allocation.items():
                item = items.get(slot)
                if item is None or item.count <= 0:
                    item = items[slot] = Item(output.id, output.aux, int(count))
                else:
                    item.count += int(count)
                changed_items[slot] = item
                output_slots.add(slot)
        for allocation in fluid_inputs:
            for slot, count in allocation.items():
                reduced_fluids[slot] = reduced_fluids.get(slot, 0) + count
        for (_, output), allocation in zip(plan.outputs.get(CategoryType.FLUID, ()), fluid_outputs):
            if not allocation or (output.prob != 1 and random.random() > output.prob):
                continue
            for slot, count in allocation.items():
                previous = added_fluids.get(slot)
                added_fluids[slot] = (output.id, count + (previous[1] if previous else 0))

        # 流体回调是同步的；先完成所有写入，再发批量通知，避免中途重入选方。
        self._applying_recipe = True
        try:
            if changed_items:
                self.SetSlotItems(changed_items)
            reduced_events = []
            for slot, count in reduced_fluids.items():
                fluid = self.fluids[slot]
                reduced_events.append((slot, fluid.fluid_id, count))
                fluid.volume -= count
            added_events = []
            for slot, (fluid_id, count) in added_fluids.items():
                fluid = self.fluids[slot]
                fluid.fluid_id = fluid_id
                fluid.volume += count
                added_events.append((slot, fluid_id, count))
            for index, (slot, fluid_id, count) in enumerate(reduced_events):
                self._on_reduced_fluid(slot, fluid_id, count, index == len(reduced_events) - 1)
            for index, (slot, fluid_id, count) in enumerate(added_events):
                self._on_added_fluid(slot, fluid_id, count, index == len(added_events) - 1)
            if output_slots:
                self.FlushOutputSlots(sorted(output_slots))
        finally:
            self._applying_recipe = False
        return True
