# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery, Upgraders
from skybluetech_scripts.skybluetech.common.mini_jei.core import (
    CategoryType,
    RecipesCollection,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    MachineRecipe,
    MachineRecipeBase,
)
from skybluetech_scripts.tooldelta.define import Item

from .item_container import ItemContainer
from .multi_fluid_container import MultiFluidContainer
from .processor_base import ProcessorBase
from .upgrade_control import UpgradeControl


class Processor(ProcessorBase):
    """
    配方处理器机器基类; 依赖的流体容器应放在 Processor 后面,
    使其在 super() 返回、开始匹配配方前完成初始化。

    目前支持处理 (记得把对应的 process_xxx 设为 True):
        - 物品
        - 流体
    """

    dump_progress_to_block_entity_data = True
    recipes = RecipesCollection("???")  # type: RecipesCollection[MachineRecipe]
    "机器配方, 改变配方表时记得重置工作进度"
    energy_mode = (0, 0, 0, 0, 0, 0)
    allow_upgraders = frozenset({
        Upgraders.BASIC_SPEED_UPGRADER,  
        Upgraders.BASIC_ENERGY_UPGRADER,
        Upgraders.GENERIC_AUTO_EJECTION,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Processor, self).__init__(dim, x, y, z, block_entity_data)
        if self.current_recipe is not None:
            self.SetProcessTicks(self.current_recipe.tick_duration)
            self.SetPower(self.current_recipe.power_cost)
            self.update_gui()
        self.handler.SubscribeOnTicking(self._processor_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._processor_on_slot_update)
        self.handler.SubscribeOnAddedFluid(self._processor_on_added_fluid)
        self.handler.SubscribeOnReducedFluid(self._processor_on_reduced_fluid)

    def _processor_on_ticking(self):
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


    def GetProgressPercent(self):
        r = self.current_recipe
        if r is None:
            return 0
        return 1 - float(self.ticks_left) / r.tick_duration

    # === item processor special ===
    def _processor_on_slot_update(self, slot_pos):
        # type: (int) -> None
        if self._applying_recipe or self.InUpgradeSlot(slot_pos):
            return
        if self.process_item:
            if slot_pos in self.item_output_slots and self.HasDeactiveFlag(
                flags.DEACTIVE_FLAG_OUTPUT_FULL
            ):
                self.start_next()
                return
            elif slot_pos in self.item_input_slots:
                self.recheck_recipe()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._processor_is_valid_input(slot, item),
        )
        return all(results)

    def _processor_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot in self.item_output_slots:
            return False
        return self._recipe_accepts_input(
            CategoryType.ITEM, slot, item.id, item.newAuxValue
        )

    # === fluid processor special ===
    def _processor_on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        if self._applying_recipe or not is_final or not isinstance(self, MultiFluidContainer):
            return
        if slot in self.fluid_input_slots and self.HasDeactiveFlag(
            flags.DEACTIVE_FLAG_NO_RECIPE
        ):
            self.recheck_recipe()

    def _processor_on_reduced_fluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
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
    def recheck_recipe(self):
        _, recipe = self.get_recipe()
        if recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            self.current_recipe = None
            self.ResetProgress()
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            if not recipe.equals(self.current_recipe):
                self.start_next(recipe)
            elif self.HasDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL):
                self.start_next(recipe)

    def run_once(self):
        "进行一次配方产出"
        _, recipe = self.get_recipe()
        if recipe is None:
            # 原生槽位变更通知延后一帧；结算可能早于通知到达。
            self.current_recipe = None
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return False
        if not recipe.equals(self.current_recipe):
            # 换料后不能沿用上一配方的进度直接产出，交给 start_next 开新批。
            return False
        if not self.can_output(recipe):
            return False
        # 专用机器的 finish_recipe 仍可能沿用无返回值的旧接口。
        return self.finish_recipe(recipe) is not False

    def start_next(self, _recipe=None):
        # type: (MachineRecipeBase | None) -> None
        "开始运行配方"
        if _recipe is None:
            _, recipe = self.get_recipe()
            if recipe is None:
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
                self.current_recipe = None
                return
            else:
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        else:
            recipe = _recipe
        if not isinstance(recipe, MachineRecipe):
            raise ValueError(
                "Processor %s run recipe %s not MachineRecipe"
                % (self.__class__.__name__, recipe.__class__.__name__)
            )
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        self.ResetProgress()
        if not self.can_output(recipe):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
        self.SetPower(recipe.power_cost)
        if not self.PowerEnough():
            return
        self.CallSync()

    def finish_recipe(self, recipe):
        # type: (MachineRecipeBase) -> bool
        return self._apply_recipe(recipe)
