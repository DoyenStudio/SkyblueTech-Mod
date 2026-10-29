# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item

from .basic.item_container import ItemContainer
from ...common.define import flags
from ...common.define.id_enum import Machinery
from .basic import (
    GUIControl,
    UpgradeControl,
)
from .core import RegisterMachine

# 没能转换的原因 (互斥): 没有输入 / 没有模板或物品与模板不符 / 产出槽放不下
IDLE_FLAGS = (
    flags.DEACTIVE_FLAG_NO_INPUT,
    flags.DEACTIVE_FLAG_NO_RECIPE,
    flags.DEACTIVE_FLAG_OUTPUT_FULL,
)


class TransInfo:
    def __init__(self, id, name, aux, damage):
        # type: (str, str, int, int) -> None
        self.c_id = id.split(":")[1]
        self.c_name = self._process_name(name)
        self.c_aux = aux
        self.c_damage = damage

    @staticmethod
    def _process_name(name):
        # type: (str) -> str
        if name[0] == "§":
            name = name[2:]
        if name[-2:] == "§r":
            name = name[:-2]
        return name

    def like(self, other):
        if not isinstance(other, TransInfo):
            return False
        return (self.c_id == other.c_id or self.c_name == other.c_name) and (
            self.c_aux == other.c_aux and self.c_damage == other.c_damage
        )


@RegisterMachine
class LexicalTransmuter(UpgradeControl, GUIControl):
    block_name = Machinery.LEXICAL_TRANSMUTER
    item_input_slots = (0,)
    item_output_slots = (1,)
    template_slot = 2
    upgrade_slot_start = 3
    is_non_energy_machine = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(LexicalTransmuter, self).__init__(dim, x, y, z, block_entity_data)
        self.template_item_trans_info = None
        self.template_item = None
        self.make_dirty()
        self.handler.SubscribeOnSlotUpdate(self._lexical_transmuter_on_slot_update)
        self.handler.SubscribeOnInvalidateCaches(self._lexical_transmuter_on_invalidate_caches)

    def _lexical_transmuter_on_slot_update(self, slot):
        if slot == 0:
            self._empty = self.GetSlotItem(0) is None
        self.make_dirty(slot)

    def _lexical_transmuter_on_invalidate_caches(self):
        self.make_dirty()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._lexical_transmuter_is_valid_input(slot, item),
        )
        return all(results)

    def _lexical_transmuter_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot == 2:
            return item.userData is None
        return slot == 0

    def make_dirty(self, slot=None):
        # type: (int | None) -> None
        if slot is None or slot == self.template_slot:
            self.refresh_template_info()
        self.run_once()

    def set_idle_reason(self, reason):
        # type: (int) -> None
        "没能转换的原因 (0 = 已转换); 只在原因变化时改停机标志, 状态灯与提示圈随之更新。"
        for flag in IDLE_FLAGS:
            self.UpdateDeactiveFlag(flag, flag == reason)

    def run_once(self):
        input_item = self.GetSlotItem(0)
        if input_item is None:
            self.set_idle_reason(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        if self.template_item_trans_info is None or self.template_item is None:
            self.set_idle_reason(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        output_item = self.GetSlotItem(1)
        if output_item is not None:
            if not output_item.CanMerge(self.template_item):
                self.set_idle_reason(flags.DEACTIVE_FLAG_OUTPUT_FULL)
                return
            if output_item.StackFull():
                self.set_idle_reason(flags.DEACTIVE_FLAG_OUTPUT_FULL)
                return
        input_item_trans_data = TransInfo(
            input_item.id,
            input_item.GetBasicInfo().itemName,
            input_item.newAuxValue,
            input_item.durability or 0,
        )
        template_item_basic_info = self.template_item.GetBasicInfo()
        if not input_item_trans_data.like(self.template_item_trans_info):
            self.set_idle_reason(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        output_item_count = output_item.count if output_item is not None else 0
        after_count = input_item.count + output_item_count
        if after_count > template_item_basic_info.maxStackSize:
            overflow_count = after_count - template_item_basic_info.maxStackSize
            after_count = template_item_basic_info.maxStackSize
        else:
            overflow_count = 0
        if output_item is None:
            output_item = self.template_item.copy()
            output_item.count = after_count
        else:
            output_item.count = after_count
        # 先清掉待机原因: 下面写槽位触发的槽位更新会再跑一次 run_once, 由它给出转换后的状态
        self.set_idle_reason(0)
        input_item.count = overflow_count
        self.SetSlotItem(0, input_item)
        self.SetSlotItem(1, output_item)
        self.FlushOutputSlots([1])

    def refresh_template_info(self):
        template_item = self.GetSlotItem(self.template_slot)
        if template_item is None:
            self.template_item_trans_info = None
            self.template_item = None
            return
        self.template_item_trans_info = TransInfo(
            template_item.id,
            template_item.GetBasicInfo().itemName,
            template_item.newAuxValue,
            template_item.durability or 0,
        )
        self.template_item = template_item
