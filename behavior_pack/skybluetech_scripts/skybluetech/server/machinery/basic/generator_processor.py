# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_TICKS_LEFT
from skybluetech_scripts.skybluetech.common.mini_jei.core import (
    CategoryType,
    RecipesCollection,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    GeneratorRecipe,
    MachineRecipeBase,
)
from skybluetech_scripts.tooldelta.define import Item

from .item_container import ItemContainer
from .base_generator import BaseGenerator
from .base_speed_control import BaseSpeedControl
from .multi_fluid_container import MultiFluidContainer
from .processor_base import ProcessorBase
from .upgrade_control import UpgradeControl

K_OUTPUT_POWER = "st:output_power"
K_RECIPE_INDEX = "st:recipe_index"
K_GENERATED_RF = "st:generated_rf"


class GeneratorProcessor(ProcessorBase, BaseGenerator):
    """
    按给定配方运行的发电机基类。

    目前支持处理 (记得把对应的 process_xxx 设为 True):
        - 物品
        - 流体
    """

    dump_progress_to_block_entity_data = True
    recipes = RecipesCollection("???")  # type: RecipesCollection[GeneratorRecipe]
    "机器配方, 改变配方表时记得重置工作进度"
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    allow_upgraders = frozenset()

    def __init__(self, dim, x, y, z, block_entity_data):
        saved_ticks = block_entity_data[K_TICKS_LEFT]
        super(GeneratorProcessor, self).__init__(dim, x, y, z, block_entity_data)
        if self.recipe_index is not None:
            self.SetProcessTicks(self.current_recipe.tick_duration)
            # 保留已付费批次的零进度，避免基类初始化或停机通知覆盖存档。
            self.ticks_left = (
                self.origin_process_ticks if saved_ticks is None
                else max(0, min(self.origin_process_ticks, saved_ticks))
            )
            if self.generated_rf is None:
                # 旧开发存档没有累计量，只能按已量化的进度估算一次。
                self.generated_rf = self._generated_rf_target()
        # 发电与进度必须在同一个回调内结算，不能先发电再判断配方是否完成。
        self.handler.UnsubscribeOnTicking(self._base_generator_on_ticking)
        self.handler.SubscribeOnTicking(self._generator_processor_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._generator_processor_on_slot_update)
        self.handler.SubscribeOnAddedFluid(self._generator_processor_on_added_fluid)
        self.handler.SubscribeOnReducedFluid(self._generator_processor_on_reduced_fluid)
        if self.current_recipe is not None:
            self.start_next()
        else:
            self.SetOutputPower(0)

    def _base_speed_control_set_deactive_flag(self, flag, flush=True):
        # 输入已经扣除；任何停机原因都不能把这批燃料的进度重新充满。
        if self.recipe_index is None:
            BaseSpeedControl._base_speed_control_set_deactive_flag(self, flag, flush)

    def _generator_processor_on_ticking(self):
        if not self.IsActive():
            # 停机时仍允许基类向邻居输出已经储存的能量。
            BaseGenerator._base_generator_on_ticking(self)
            return
        remaining = self.reduce_ticks
        while self.IsActive():
            if self.current_recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                break
            if self.ticks_left > 0:
                if remaining <= 0:
                    break
                consumed = min(remaining, self.ticks_left)
                self.ticks_left -= consumed
                remaining -= consumed
                # 进度重载会量化为 float32，不能用它反推上次实际已发出的整数 RF。
                emitted = self.generated_rf
                target = self._generated_rf_target()
                generated = int(max(0, target - emitted))
                self.generated_rf = emitted + generated
                self.SetOutputPower(generated)
                try:
                    BaseGenerator._base_generator_on_ticking(self)
                finally:
                    self.SetOutputPower(self.generator_output_power)
            if self.ticks_left <= 0:
                if not self.run_once():
                    break
                self.start_next()
            if remaining <= 0:
                break
        self.CallSync()

    def _generated_rf_target(self):
        recipe = self.current_recipe
        budget = recipe.output_power * recipe.tick_duration
        if self.ticks_left <= 0:
            return budget
        return min(
            budget,
            int(recipe.output_power * (recipe.tick_duration - self.ticks_left)),
        )


    # === item processor special ===
    def _generator_processor_on_slot_update(self, slot_pos):
        # type: (int) -> None
        if self._applying_recipe or self.InUpgradeSlot(slot_pos):
            return
        if self.process_item:
            if slot_pos in self.item_output_slots and self.HasDeactiveFlag(
                flags.DEACTIVE_FLAG_OUTPUT_FULL
            ):
                self.start_next()
                return
            elif slot_pos in self.item_input_slots and self.recipe_index is None:
                # 只有在没开始运行配方时才重新检查配方
                # 在配方开始运行后就不检查了
                self.recheck_recipe()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._generator_processor_is_valid_input(slot, item),
        )
        return all(results)

    def _generator_processor_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot in self.item_output_slots:
            return False
        return self._recipe_accepts_input(
            CategoryType.ITEM, slot, item.id, item.newAuxValue
        )

    # === fluid processor special ===
    def _generator_processor_on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if self._applying_recipe or not is_final or not isinstance(self, MultiFluidContainer):
            return
        if slot in self.fluid_input_slots and self.HasDeactiveFlag(
            flags.DEACTIVE_FLAG_NO_RECIPE
        ):
            self.recheck_recipe()

    def _generator_processor_on_reduced_fluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if self._applying_recipe or not is_final or not isinstance(self, MultiFluidContainer):
            return
        if slot in self.fluid_output_slots:
            if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                self.start_next()
                return
        elif slot in self.fluid_input_slots:
            self.recheck_recipe()

    # ======
    def get_recipe(self):
        if self.recipe_index is not None:
            return self.recipe_index, self.recipes[self.recipe_index]
        else:
            return ProcessorBase.get_recipe(self)

    def recheck_recipe(self):
        recipe_index, recipe = self.get_recipe()
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
            self.ResetProgress()
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            if self.recipe_index is None or not recipe.equals(self.current_recipe):
                self.start_next(recipe_index, recipe)
            elif self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                self.start_next()

    def run_once(self):
        _, recipe = self.get_recipe()
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return False
        if not self.can_output(recipe) or not self.finish_recipe(recipe):
            # 已完成但被堵住的批次仍保留索引，解堵只补产物，不再发一轮电。
            self.ticks_left = 0
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return False
        return True

    def start_next(self, recipe_index=0, _recipe=None):
        # type: (int, MachineRecipeBase | None) -> None
        "开始运行配方，已扣料的批次只恢复运行或补交产物。"
        if _recipe is None:
            recipe_index, recipe = self.get_recipe()
            if recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                self.current_recipe = None
                self.SetOutputPower(0)
                return
        else:
            recipe = _recipe
        if not isinstance(recipe, GeneratorRecipe):
            raise ValueError(
                "Processor %s run recipe not GeneratorRecipe" % self.__class__.__name__
            )
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        if self.recipe_index is None:
            self.ResetProgress()
        self.generator_output_power = recipe.output_power
        self.SetOutputPower(self.generator_output_power)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not self.can_output(recipe):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        if self.recipe_index is not None:
            if self.ticks_left <= 0:
                if self.run_once():
                    self.start_next()
                return
        else:
            if not self.start_recipe(recipe_index, recipe):
                self.current_recipe = None
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                return
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
        self.CallSync()

    def start_recipe(self, recipe_index, recipe):
        # type: (int, MachineRecipeBase) -> bool
        # 必须在扣料通知前标记已付费，恢复和重查都不能再匹配已消耗的输入。
        self.recipe_index = recipe_index
        self.generated_rf = 0
        if self._apply_recipe(recipe, produce_outputs=False):
            return True
        self.recipe_index = None
        return False

    def finish_recipe(self, recipe):
        # type: (MachineRecipeBase) -> bool
        if not self._apply_recipe(recipe, consume_inputs=False):
            return False
        self.recipe_index = None
        return True

    @property
    def generator_output_power(self):
        # type: () -> int
        return self.bdata[K_OUTPUT_POWER] or 0

    @generator_output_power.setter
    def generator_output_power(self, value):
        # type: (int) -> None
        self.bdata[K_OUTPUT_POWER] = value

    @property
    def generated_rf(self):
        record = self.bdata[K_GENERATED_RF]
        if record is None:
            return None
        return (record["high"] << 31) + record["low"]

    @generated_rf.setter
    def generated_rf(self, value):
        # 总量可在内存中成为 long；NBT 只接收两个合法的非负 int。
        low = int(value & 0x7fffffff)
        high = int(value >> 31)
        if not (0 <= low <= 0x7fffffff and 0 <= high <= 0x7fffffff):
            raise ValueError("Generated RF exceeds two 31-bit integers")
        self.bdata[K_GENERATED_RF] = {"low": low, "high": high}

    @property
    def recipe_index(self):
        # type: () -> int | None
        return self.bdata[K_RECIPE_INDEX]

    @recipe_index.setter
    def recipe_index(self, value):
        # type: (int | None) -> None
        self.bdata[K_RECIPE_INDEX] = value
