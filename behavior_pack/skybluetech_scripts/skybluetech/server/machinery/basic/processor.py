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
from .slot_reads import SlotReads, accepts_slot_reads
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
            self._check_output()
            self.update_gui()
        self.handler.SubscribeOnTicking(self._processor_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._processor_on_slot_update)
        self.handler.SubscribeOnAddedFluid(self._processor_on_added_fluid)
        self.handler.SubscribeOnReducedFluid(self._processor_on_reduced_fluid)

    def _processor_on_ticking(self):
        if not self.IsActive():
            return
        if self.current_recipe is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        if not self._check_output():
            return
        # 每 tick 只推进、扣电一次；已完成但尚未结算的批次不再扣电。
        if self.ticks_left > 0 and not self.ProcessOnce():
            self.CallSync()
            return
        while self.IsActive() and self.ticks_left <= 0:
            remaining = -self.ticks_left
            self.ticks_left = 0
            if not self.run_once():
                # 同配方结算失败保留完成进度；换料则重新开批。
                self.recheck_recipe()
                break
            self.start_next(check_power=remaining <= 0)
            if remaining <= 0 or not self.IsActive() or self.current_recipe is None:
                break
            # 剩余加工量已在本 tick 付过电费，下一批不能再次扣电。
            self.ticks_left -= remaining
        self.CallSync()

    def ProcessOnce(self):
        """每 tick 调用一次，推进并返回是否可结算；覆写时不得重置批次进度。"""
        if not self.PowerEnough():
            return False
        self.ReducePower()
        self.ticks_left -= self.reduce_ticks
        return self.ticks_left <= 0

    def _check_output(self):
        can_output = self.can_output(self.current_recipe)
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, not can_output)
        return can_output

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
                self.recheck_recipe()
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
                self.recheck_recipe()
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
            else:
                self._check_output()

    def run_once(self):
        "进行一次配方产出，返回是否成功；失败不得开始下一批。"
        reads = SlotReads(self)
        _, recipe = reads.call(self.get_recipe)
        if recipe is None:
            # 原生槽位变更通知延后一帧；结算可能早于通知到达。
            self.current_recipe = None
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return False
        if not recipe.equals(self.current_recipe):
            # 换料后不能沿用上一配方的进度直接产出，交给 start_next 开新批。
            return False
        if not reads.call(self.can_output, recipe):
            return False
        # 专用机器的 finish_recipe 仍可能沿用无返回值的旧接口。
        return reads.call(self.finish_recipe, recipe) is not False

    def start_next(self, _recipe=None, check_power=True):
        # type: (MachineRecipeBase | None, bool) -> None
        "开始运行配方；仅在使用本 tick 已付费的剩余加工量时跳过电量检查。"
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
        self._check_output()
        self.SetPower(recipe.power_cost)
        if check_power and not self.PowerEnough():
            return
        self.CallSync()

    @accepts_slot_reads
    def finish_recipe(self, recipe, slot_reads=None):
        return (slot_reads or SlotReads(self)).call(self._apply_recipe, recipe)
