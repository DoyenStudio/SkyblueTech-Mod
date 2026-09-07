# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import FACING_DXYZ
from skybluetech_scripts.skybluetech.common.define.id_enum.items import Upgraders
from skybluetech_scripts.skybluetech.common.machinery_def.upgraders import (
    POWER_NEGATIVE,
    POWER_POSITIVE,
    SPEED_NEGATIVE,
    SPEED_POSITIVE,
)
from skybluetech_scripts.tooldelta.api.server import SpawnDroppedItem
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server.item import (
    PlayerTryPutCustomContainerItemServerEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from .base_machine import BaseMachine
from .item_container import ItemContainer
from .sp_control import SPControl


class UpgradeControl(ItemContainer, SPControl):
    """
    代表可接受升级卡的机器基类。

    派生自:
        `ItemContainer`
        `SPControl`

    类属性:
        upgrade_slot_start (int): 升级槽起始槽位
        upgrade_slots (int): 升级槽数量
        allow_upgraders (frozenset[str]): 可接受的机器升级卡ID。

    覆写:
        - `__init__`
        - `IsValidInput`
        - `OnCustomCotainerPutItem`
        - `OnSlotUpdate`
        - `AddPower`
        - `SetDeactiveFlag`
    """

    upgrade_slot_start = 2  # type: int
    upgrade_slots = 4  # type: int
    allow_upgraders = frozenset()  # type: set[str] | frozenset[str]

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._basic_max_rf_store = self.store_rf_max
        self._power_cost_relative = 1.0
        self.UpdateUpgraders(self.GetAllUpgraders())

    def InUpgradeSlot(self, slot):
        # type: (int) -> bool
        return (
            slot >= self.upgrade_slot_start
            and slot < self.upgrade_slot_start + self.upgrade_slots
        )

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return (
            slot >= self.upgrade_slot_start
            and slot < self.upgrade_slot_start + self.upgrade_slots
            and self._item_is_valid_upgrader(item)
            and not self._other_slot_has_same_upgrader(slot, item.id)
        )

    def OnCustomCotainerPutItem(self, event):
        # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
        "超类方法, 处理玩家向升级槽放入物品的事件。"
        if not self.InUpgradeSlot(event.collectionIndex):
            return ItemContainer.OnCustomCotainerPutItem(self, event)
        if not self._item_is_valid_upgrader(event.item):
            event.cancel()
            return
        # 升级槽已有物品则禁止放入
        existing = self.GetSlotItem(event.collectionIndex)
        if existing is not None:
            event.cancel()
            return
        # 不能在不同槽位放入相同的升级
        if self._other_slot_has_same_upgrader(event.collectionIndex, event.item.id):
            event.cancel()
            return

    def ReducePower(self, rf=None, bypass_upgraders=False):
        # type: (int | None, bool) -> None
        "PowerControl 方法, 由 UpgradeControl 覆写"
        if rf is None:
            rf = self.running_power
        if not bypass_upgraders:
            rf = round(rf * self._power_cost_relative)
        BaseMachine.ReducePower(self, rf)

    def PowerEnough(self):
        # type: () -> bool
        """
        PowerControl 方法, 由 UpgradeControl 覆写

        如果能量不足时先尝试向电网索取能源, 后自动将 flag 设置为缺少能源
        """
        res = self.store_rf >= round(self.running_power * self._power_cost_relative)
        if res:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        else:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        return res

    def OnSlotUpdate(self, slot):
        # type: (int) -> None
        "超类方法更新升级槽数据。"
        if (
            slot < self.upgrade_slot_start
            or slot >= self.upgrade_slot_start + self.upgrade_slots
        ):
            return
        # 如果一次性放入多个升级，多余升级变成掉落物，只保留一个
        item = self.GetSlotItem(slot)
        if item is not None and item.count > 1:
            extra_item = item.copy()
            extra_item.count = item.count - 1
            px, py, pz = self.xyz
            SpawnDroppedItem(
                self.dim,
                (px + 0.5, py + 0.5, pz + 0.5),
                extra_item,
            )
            item.count = 1
            self.SetSlotItem(slot, item)
        self.UpdateUpgraders(self.GetAllUpgraders())

    def GetAllUpgraders(self):
        # type: () -> dict[str, int]
        """
        获取所有升级卡。

        Returns:
            dict[str, int]: 升级卡字典, 键为升级卡 ID, 值为升级卡数量。
        """
        res = {}  # type: dict[str, int]
        for i in range(
            self.upgrade_slot_start, self.upgrade_slot_start + self.upgrade_slots
        ):
            item = self.GetSlotItem(i)
            if item is None:
                continue
            res[item.id] = item.count
        return res

    def FlushOutputSlots(self, slots):
        # type: (list[int]) -> None
        if self.HasUpgrader(Upgraders.GENERIC_AUTO_EJECTION):
            self._auto_eject_item(slots)

    def OutputItem(self, item):
        # type: (Item) -> Item | None
        rest = ItemContainer.OutputItem(self, item)
        self.FlushOutputSlots(list(self.output_slots))
        return rest

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
            speed_pos += SPEED_POSITIVE.get(upgrader, 0) * count
            speed_neg += SPEED_NEGATIVE.get(upgrader, 0) * count
            # power
            power_pos += POWER_POSITIVE.get(upgrader, 0) * count
            power_neg += POWER_NEGATIVE.get(upgrader, 0) * count
        self.SetSpeedRelative(speed_pos / speed_neg)
        self._power_cost_relative = power_pos / power_neg

    def HasUpgrader(self, item_id):
        # type: (str) -> bool
        return item_id in self._upgraders

    def _other_slot_has_same_upgrader(self, slot, item_name):
        # type: (int, str) -> bool
        slot_range = range(
            self.upgrade_slot_start, self.upgrade_slot_start + self.upgrade_slots
        )
        for i in slot_range:
            slotitem = self.GetSlotItem(i)
            if (
                slotitem is not None
                and i != slot
                and slotitem.id == item_name
                and i != slot
            ):
                return True
        return False

    def _item_is_valid_upgrader(self, item):
        # type: (Item) -> bool
        return item.id in self.allow_upgraders


    def _auto_eject_item(self, slots):
        # type: (list[int]) -> None
        """尝试把指定输出槽中的物品送入六面相邻容器。"""
        from ...transmitters.cable.logic import PushItemToGenericContainerEasy

        for slot in slots:
            if slot not in self.output_slots:
                continue
            item = self.GetSlotItem(slot, get_user_data=True)
            if item is None:
                continue
            rest = item
            for face, (dx, dy, dz) in enumerate(FACING_DXYZ):
                rest = PushItemToGenericContainerEasy(
                    self.dim,
                    (self.x + dx, self.y + dy, self.z + dz),
                    face,
                    rest,
                )
                if rest is None:
                    break
            if rest is None:
                ItemContainer.SetSlotItem(self, slot, None)
            elif rest.count != item.count:
                ItemContainer.SetSlotItem(self, slot, rest)
