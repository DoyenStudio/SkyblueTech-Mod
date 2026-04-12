# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.mini_jei.core import CategoryType, RecipesCollection
from ....common.mini_jei.machinery import MachineRecipeBase, GeneratorRecipe
from ....common.define import flags as flags
from .base_generator import BaseGenerator
from .base_speed_control import BaseSpeedControl
from .multi_fluid_container import MultiFluidContainer
from .upgrade_control import UpgradeControl
from .processor_base import ProcessorBase

K_OUTPUT_POWER = "output_power"


class GeneratorProcessor(BaseGenerator, UpgradeControl, ProcessorBase):
    """
    按给定配方运行的发电机基类。

    目前支持处理 (记得把对应的 process_xxx 设为 True):
        - 物品
        - 流体
    """

    recipes = RecipesCollection("???")  # type: RecipesCollection[GeneratorRecipe]
    "机器配方, 改变配方表时记得重置工作进度"
    energy_mode = (0, 0, 0, 0, 0, 0)
    allow_upgrader_tags = set()

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.SetOutputPower(self.generator_output_power)

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        while self.IsActive():
            if self.current_recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                return
            if BaseSpeedControl.ProcessOnce(self):
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
        recipe = self.get_recipe()
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
            self.ResetProgress()
        elif not recipe.equals(self.current_recipe):
            self.start_next(recipe)
        elif self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
            self.start_next()

    def run_once(self):
        inputs = self.GetInputSlotItems()
        outputs = self.GetOutputSlotItems()
        recipe = self.get_recipe()
        if recipe is None:
            # cannot reach
            raise ValueError("Recipe ERROR")
        if not self.can_output(recipe):
            return
        inputs.update(outputs)
        self.finish_recipe(inputs, recipe)

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
        if not isinstance(recipe, GeneratorRecipe):
            raise ValueError(
                "Processor %s run recipe not GeneratorRecipe" % self.__class__.__name__
            )
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        self.ResetProgress()
        if not self.can_output(recipe):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        self.ResetDeactiveFlags()
        self.generator_output_power = recipe.output_power
        self.SetOutputPower(self.generator_output_power)
        self.CallSync()

    @property
    def generator_output_power(self):
        # type: () -> int
        return self.bdata[K_OUTPUT_POWER] or 0

    @generator_output_power.setter
    def generator_output_power(self, value):
        # type: (int) -> None
        self.bdata[K_OUTPUT_POWER] = value
