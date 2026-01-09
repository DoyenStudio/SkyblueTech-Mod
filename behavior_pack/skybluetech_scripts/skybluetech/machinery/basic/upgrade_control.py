# coding=utf-8
#
from skybluetech_scripts.tooldelta.define.item import Item
from ...machinery_def.upgraders import *
from .base_machine import BaseMachine
from .item_container import ItemContainer
from .sp_control import SPControl


class UpgradeControl(ItemContainer, SPControl):
    """
    代表可接受升级卡的机器基类。
    
    派生自 `ItemContainer`, `SPControl`

    需要调用 `__init__()` [基调用]
    
    覆写: `IsValidInput`, `OnSlotUpdate`, `OnLoad`[基调用], `Dump`[基调用], `AddPower`[基调用], `SetDeactiveFlag`[基调用]
    """
    upgrade_slot_start = 2 # type: int
    upgrade_slots = 4 # type: int
    allow_upgrader_tags = set() # type: set[str]
    "可接受的机器升级卡标签。"

    def __init__(self, dim, x, y, z, block_entity_data):
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        SPControl.__init__(self, dim, x, y, z, block_entity_data)
        self._basic_max_rf_store = self.store_rf_max
        self._origin_power = self.running_power
        self.UpdateUpgraders(self.GetAllUpgraders())

    def InUpgradeSlot(self, slot):
        # type: (int) -> bool
        return slot >= self.upgrade_slot_start and slot < self.upgrade_slot_start + self.upgrade_slots

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return (
            slot >= self.upgrade_slot_start
            and slot < self.upgrade_slot_start + self.upgrade_slots
            and self.itemIsValidUpgrader(item)
            and item.count == 1
            and not self.otherSlotHasSameUpgrader(slot, item.id)
        )

    def OnSlotUpdate(self, slot):
        # type: (int) -> None
        if slot < self.upgrade_slot_start or slot >= self.upgrade_slot_start + self.upgrade_slots:
            return
        self.UpdateUpgraders(self.GetAllUpgraders())

    def GetAllUpgraders(self):
        # type: () -> dict[str, int]
        res = {} # type: dict[str, int]
        for i in range(self.upgrade_slot_start, self.upgrade_slot_start + self.upgrade_slots):
            item = self.GetSlotItem(i)
            if item is None:
                continue
            res[item.id] = item.count
        return res

    def UpdateUpgraders(self, upgraders):
        # type: (dict[str, int]) -> None
        "超类方法更新基本的速度和能量升级处理。超类方法作进一步处理"
        self._upgraders = upgraders
        speed_pos = 1.0
        speed_neg = 1.0
        power_pos = 1.0
        power_neg = 1.0
        for upgrader, count in upgraders.items():
            # speed
            speed_add, power_redu = SPEED_UPGRADER_MAPPINGS.get(upgrader, (0, 0))
            speed_pos += speed_add * count
            power_pos += power_redu * count
            # power
            power_neg += POWER_UPGRADER_MAPPINGS.get(upgrader, 0) * count
        self.SetSpeedRelative(speed_pos / speed_neg)
        self.SetPower(int(self._origin_power * power_pos / power_neg))

    def HasUpgrader(self, item_id):
        # type: (str) -> bool
        return item_id in self._upgraders

    def otherSlotHasSameUpgrader(self, slot, item_name):
        # type: (int, str) -> bool
        slot_range = range(self.upgrade_slot_start, self.upgrade_slot_start + self.upgrade_slots)
        for i in slot_range:
            slotitem = self.GetSlotItem(i)
            if slotitem is not None and i != slot and slotitem.id == item_name and i != slot:
                return True
        return False

    def itemIsValidUpgrader(self, item):
        # type: (Item) -> bool
        return any(tag in self.allow_upgrader_tags for tag in item.GetBasicInfo().tags)
