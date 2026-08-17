# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define import flags
from ...common.define.id_enum.machinery import Machinery
from ...common.machinery_def.precision_cutter import (
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    CUTTER_LEVEL_MAPPING,
    recipes as Recipes,
)
from ...common.mini_jei.machinery.precision_cutter import PrecisionCutterRecipe
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class PrecisionCutter(MultiFluidContainer, Processor):
    """精密切割机: 1 流体槽 + 5 物品槽(2 输入 / 3 输出) + 4 升级槽。

    槽位1为锯片槽, 只接受 cutter 表中的锯片; 运行配方要求锯片等级不低于
    配方最低等级, 每次完成配方后按配方耐久消耗值扣减锯片耐久。
    """

    block_name = Machinery.PRECISION_CUTTER
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    input_slots = (0, 1)
    output_slots = (2, 3, 4)
    cutter_slot = 1
    # 5 个物品槽用作输入/输出, 另外 4 个槽位(5-8)作为升级槽
    upgrade_slot_start = 5
    upgrade_slots = 4
    fluid_slot_start = 5
    fluid_input_slots = {5}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot == self.cutter_slot:
            return item.id in CUTTER_LEVEL_MAPPING
        return Processor.IsValidInput(self, slot, item)

    def get_recipe(self):
        # type: () -> tuple[int, PrecisionCutterRecipe | None]
        "在基类配方匹配的基础上, 额外要求槽位1的锯片等级满足配方最低等级。"
        recipe_idx, recipe = Processor.get_recipe(self)
        if not isinstance(recipe, PrecisionCutterRecipe): # recipe is None
            return recipe_idx, None
        if not self.cutter_meets_requirement(recipe):
            return recipe_idx, None
        return recipe_idx, recipe

    def run_once(self):
        "覆写基类: 产出前后都校验锯片, 完成一次配方后扣减锯片耐久。"
        recipe = self.current_recipe
        if recipe is None or not self.cutter_meets_requirement(recipe):
            self.current_recipe = None
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        Processor.run_once(self)
        self.consume_cutter_durability(recipe)

    def cutter_meets_requirement(self, recipe):
        # type: (PrecisionCutterRecipe) -> bool
        "槽位1存在未损坏锯片, 且锯片等级 >= 配方最低等级。"
        cutter = self.GetSlotItem(self.cutter_slot)
        if cutter is None:
            return False
        level = CUTTER_LEVEL_MAPPING.get(cutter.id, 0)
        if level <= 0:
            return False
        if recipe.cutter_level > level:
            return False
        durability = cutter.durability
        if durability is None:
            durability = cutter.GetBasicInfo().maxDurability
        return durability > 0

    def consume_cutter_durability(self, recipe):
        # type: (PrecisionCutterRecipe) -> None
        "按配方指定的锯片耐久消耗值扣减耐久, 耐久不足直接清空槽位。"
        cutter = self.GetSlotItem(self.cutter_slot, get_user_data=True)
        if cutter is None:
            return
        durability = cutter.durability
        if durability is None:
            durability = cutter.GetBasicInfo().maxDurability
        durability -= recipe.cutter_durability_cost
        if durability <= 0:
            self.SetSlotItem(self.cutter_slot, None)
        else:
            cutter.durability = durability
            self.SetSlotItem(self.cutter_slot, cutter)

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass
