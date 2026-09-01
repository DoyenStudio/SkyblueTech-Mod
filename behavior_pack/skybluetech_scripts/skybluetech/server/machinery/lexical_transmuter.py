# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum.machinery import Machinery
from .basic import (
    GUIControl,
    RegisterMachine,
    UpgradeControl,
)


class TransInfo:
    def __init__(self, id, name):
        # type: (str, str) -> None
        self.c_id = id.split(":")[1]
        self.c_name = self._process_name(name)

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
        return self.c_id == other.c_id or self.c_name == other.c_name


@RegisterMachine
class LexicalTransmuter(GUIControl, UpgradeControl):
    block_name = Machinery.LEXICAL_TRANSMUTER
    input_slots = (0,)
    output_slots = (1,)
    template_slot = 2
    upgrade_slot_start = 3
    is_non_energy_machine = True

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.template_item_trans_info = None
        self.template_item = None
        self.make_dirty()

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot):
        if slot == 0:
            self._empty = self.GetSlotItem(0) is None
        self.make_dirty(slot)

    @SuperExecutorMeta.execute_super
    def OnInvalidateCaches(self):
        self.make_dirty()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        elif slot == 1:
            return item.userData is None
        return slot == 0

    def make_dirty(self, slot=None):
        # type: (int | None) -> None
        if slot is None or slot == self.template_slot:
            self.refresh_template_info()
        self.run_once()

    def run_once(self):
        input_item = self.GetSlotItem(0)
        if input_item is None:
            return
        if self.template_item_trans_info is None or self.template_item is None:
            return
        output_item = self.GetSlotItem(1)
        if output_item is not None:
            if not output_item.CanMerge(self.template_item):
                return
            if output_item.StackFull():
                return
        input_item_trans_data = TransInfo(
            input_item.id, input_item.GetBasicInfo().itemName
        )
        template_item_basic_info = self.template_item.GetBasicInfo()
        if not input_item_trans_data.like(self.template_item_trans_info):
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
        input_item.count = overflow_count
        self.SetSlotItem(0, input_item)
        self.SetSlotItem(1, output_item)

    def refresh_template_info(self):
        template_item = self.GetSlotItem(self.template_slot)
        if template_item is None:
            self.template_item_trans_info = None
            self.template_item = None
            return
        self.template_item_trans_info = TransInfo(
            template_item.id, template_item.GetBasicInfo().itemName
        )
        self.template_item = template_item
