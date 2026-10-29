# coding=utf-8
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe,
)
from skybluetech_scripts.tooldelta.define import Item

from .basic.item_container import ItemContainer
from ...common.define.id_enum import Machinery
from ...common.events.machinery.electric_machinery_workstation import (
    ElectricMachineryWorkstationSelectRecipe,
)
from ...common.machinery_def.electric_machinery_workstation import (
    CRAFT_TICKS_MULTIPLIER,
    DEFAULT_POWER,
    K_OUTPUT_ITEM_ID,
    K_SELECTED_RECIPE,
    OUTPUT_SLOT,
    SOLDER_ITEM_ID,
    SOLDER_SLOT,
    STORE_RF_MAX,
    RecipesCollection,
    recipes,
)
from ...common.mini_jei import Input
from .basic import OperationListener, Processor, UpgradeControl
from .core import RegisterMachine
from .utils.bans import is_machine_banned, reject_banned_machine


def _same_input(a, b):
    # type: (Input, Input) -> bool
    "两个配方输入是否需求同一种物品(不考虑数量)。"
    return a.id == b.id and a.is_tag == b.is_tag and a.aux == b.aux


@RegisterMachine
class ElectricMachineryWorkstation(Processor, OperationListener):
    block_name = Machinery.ELECTRIC_MACHINERY_WORKSTATION
    store_rf_max = STORE_RF_MAX
    running_power = DEFAULT_POWER
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = recipes # pyright: ignore[reportAssignmentType]
    item_input_slots = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    item_output_slots = (10,)
    upgrade_slot_start = 11
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ElectricMachineryWorkstation, self).__init__(dim, x, y, z, block_entity_data)
        # 父类已加载存档配方, 清除被禁用的选择并重置加工状态。
        if is_machine_banned(self.bdata[K_SELECTED_RECIPE]):
            self.bdata[K_SELECTED_RECIPE] = None
            self.recheck_recipe()
        self.CallSync()
        self.handler.UnsubscribeOnSlotUpdate(self._processor_on_slot_update)
        self.handler.SubscribeOnSlotUpdate(self._electric_machinery_workstation_on_slot_update)
        self.handler.SubscribeOnSync(self._electric_machinery_workstation_on_sync)
        self.CallSync()

    def get_recipe(self):
        # 配方取自机件加工台(九宫格, 未使用的位置必须为空), 另需焊锡槽有焊锡
        items = self.GetInputSlotItems()
        solder = items.get(SOLDER_SLOT)
        if solder is None or solder.id != SOLDER_ITEM_ID:
            return 0, None
        recipe = self._get_selected_recipe()
        if recipe is None:
            return 0, None
        for slot in range(SOLDER_SLOT):
            required = recipe.input_items.get(slot)
            item = items.get(slot)
            if required is None:
                if item is not None:
                    return 0, None
            elif (
                item is None
                or not required.match_item_id(item.id)
                or item.count < required.count
            ):
                return 0, None
        # 机件加工台的配方不描述本机的加工时长与耗能, 这里换算后写回配方对象
        recipe.tick_duration = recipe.craft_times * CRAFT_TICKS_MULTIPLIER
        recipe.power_cost = DEFAULT_POWER
        return 0, recipe

    def can_output(self, recipe):
        # type: (MachineryWorkstationRecipe) -> bool
        # 产物在本机的槽 10, 而配方里的产物定义在槽 0(机件加工台的产物位置)
        item = self.GetSlotItem(OUTPUT_SLOT)
        if item is None:
            return True
        return (
            item.id == recipe.output_item_id
            and item.count + 1 <= item.GetBasicInfo().maxStackSize
        )

    def finish_recipe(self, recipe):
        # type: (MachineryWorkstationRecipe) -> None
        slotitems = self.GetInputSlotItems()
        slotitems.update(self.GetOutputSlotItems())
        for slot, required in recipe.input_items.items():
            slotitems[slot].count -= int(required.count)
        slotitems[SOLDER_SLOT].count -= 1
        output_item = slotitems.get(OUTPUT_SLOT)
        if output_item is None:
            slotitems[OUTPUT_SLOT] = Item(recipe.output_item_id, 0, 1)
        else:
            output_item.count += 1
        self.SetSlotItems(slotitems)
        self.FlushOutputSlots([OUTPUT_SLOT])

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._electric_machinery_workstation_is_valid_input(slot, item),
        )
        return all(results)

    def _electric_machinery_workstation_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        """只认配方列表中选中的那个配方在该槽位要求的物品, 未选中配方时拒绝一切输入。"""
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        if slot == SOLDER_SLOT:
            return item.id == SOLDER_ITEM_ID
        if slot in self.item_output_slots:
            return False
        recipe = self._get_selected_recipe()
        if recipe is None:
            return False
        required = recipe.input_items.get(slot)
        return required is not None and required.match_item_id(item.id)

    def separate_items(self):
        """把堆在同一槽位的原料均摊到其它需求同种原料的空槽位, 免去玩家手动拆分。"""
        recipe = self._get_selected_recipe()
        if recipe is None:
            return
        slot_inputs = {}  # type: dict[int, Input]
        for slot in self.item_input_slots:
            required = recipe.input_items.get(slot)
            if required is not None:
                slot_inputs[slot] = required
        for slot, required in slot_inputs.items():
            if self.GetSlotItem(slot) is not None:
                continue
            for src_slot, src_required in slot_inputs.items():
                if src_slot == slot or not _same_input(src_required, required):
                    continue
                src_item = self.GetSlotItem(src_slot)
                # TODO: 目前和电动合成台一样, 默认每个输入槽只需要 1 个物品: 挪 1 个, 源槽位至少留 1 个;
                # 以后要支持配方输入 count > 1 时, 再按 required.count / src_required.count 计算挪多少
                if src_item is None or src_item.count <= 1:
                    continue
                moved = src_item.copy()
                moved.count = 1
                src_item.count -= 1
                self.SetSlotItem(src_slot, src_item)
                self.SetSlotItem(slot, moved)
                break

    def _electric_machinery_workstation_on_slot_update(self, slot_pos):
        if slot_pos in self.item_input_slots:
            self.separate_items()
        Processor._processor_on_slot_update(self, slot_pos)
        self.CallSync()

    def _electric_machinery_workstation_on_sync(self):
        self.bdata[K_OUTPUT_ITEM_ID] = (
            self.current_recipe.output_item_id
            if isinstance(self.current_recipe, MachineryWorkstationRecipe)
            else None
        )

    def select_recipe(self, output_item_id):
        recipe = next(
            (r for r in self._get_machine_recipes() if r.output_item_id == output_item_id), None
        )
        if recipe is None:
            return
        self.bdata[K_SELECTED_RECIPE] = output_item_id
        self.recheck_recipe()
        self.CallSync()

    def _get_selected_recipe(self):
        # type: () -> MachineryWorkstationRecipe | None
        selected_recipe_id = self.bdata[K_SELECTED_RECIPE]
        return next(
            (
                r
                for r in self._get_machine_recipes()
                if r.output_item_id == selected_recipe_id
            ),
            None,
        )

    def _get_machine_recipes(self):
        # type: () -> RecipesCollection[MachineryWorkstationRecipe]
        # IDE TYPE CHECK
        return self.recipes # pyright: ignore[reportReturnType]


@ElectricMachineryWorkstation.ForOperation(ElectricMachineryWorkstationSelectRecipe)
def on_select_recipe(event, machine):
    # type: (ElectricMachineryWorkstationSelectRecipe, ElectricMachineryWorkstation) -> None
    if reject_banned_machine(event.player_id, event.output_item_id):
        return
    machine.select_recipe(event.output_item_id)
