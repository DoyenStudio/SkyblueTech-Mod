# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.mini_jei.core import CategoryType, RecipesCollection
from ....common.mini_jei.machinery import MachineRecipeBase
from ....common.define import flags as flags
from .gui_ctrl import GUIControl
from .multi_fluid_container import MultiFluidContainer
from .item_container import ItemContainer
from .work_renderer import WorkRenderer


class ProcessorBase(GUIControl, ItemContainer, WorkRenderer):
    """
    配方处理器基类。
    """

    process_item = False
    "是否处理物品; 输入或输出中有物品都要设为 True"
    process_fluid = False
    "是否处理流体; 输入或输出中有流体都要设为 True"

    recipes = RecipesCollection("???")  # type: RecipesCollection[MachineRecipeBase]
    "机器配方, 改变配方表时记得重置工作进度"

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        _, self.current_recipe = self.get_recipe()
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        pass

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    @SuperExecutorMeta.execute_super
    def UnsetDeactiveFlag(self, flag, flush=True):
        pass

    @SuperExecutorMeta.execute_super
    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        for recipe in self.recipes:
            slot_input = recipe.inputs.get("fluid", {}).get(slot)
            if slot_input is None:
                continue
            if slot_input.match_item_id(fluid_id):
                return True
        return False

    def get_recipe(self):
        # type: () -> tuple[int, MachineRecipeBase | None]
        for recipe_idx, recipe in enumerate(self.recipes):
            cont = False
            if self.process_item:
                inputs = self.GetInputSlotItems()
                for slot_pos, input in recipe.inputs.get(CategoryType.ITEM, {}).items():
                    item = inputs.get(slot_pos, None)
                    if item is None:
                        cont = True
                        break
                    if not input.match_item_id(item.id) or item.count < input.count:
                        cont = True
                        break
            if self.process_fluid and isinstance(self, MultiFluidContainer):
                for slot_pos, input in recipe.inputs.get(
                    CategoryType.FLUID, {}
                ).items():
                    fluid = self.fluids[slot_pos]
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
                return recipe_idx, recipe
        return (0, None)

    def can_output(self, recipe):
        # type: (MachineRecipeBase) -> bool
        outputs = recipe.outputs
        if self.process_item:
            output_slots = self.GetOutputSlotItems()
            for slot_pos, output in outputs.get(CategoryType.ITEM, {}).items():
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
        if self.process_fluid and isinstance(self, MultiFluidContainer):
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
