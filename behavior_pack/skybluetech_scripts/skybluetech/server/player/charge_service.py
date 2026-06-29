# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetAllInventoryItems,
    GetArmorSlotItems,
    SetPlayerAllItems,
)
from skybluetech_scripts.tooldelta.events.server import InventoryItemChangedServerEvent
from .base import PlayerService
from ..machinery.utils.charge import (
    ChargeItem,
    IsEnableCharge,
    GetIOPower,
    GetCharge,
    UpdateCharge,
    CanChargeInventory,
)

ItemPosType = GetMinecraftEnum().ItemPosType


class ChargeService(PlayerService):
    tick_interval = 40  # 每 40t 为玩家物品充能一次

    def __init__(self, player_id):
        # type: (str) -> None
        self._charging = True
        PlayerService.__init__(self, player_id)

    def enable_charge(self):
        self._charging = True

    def charge(self, rf, charge_inv=True, charge_armor=True, charge_charger=True):
        # type: (int, bool, bool, bool) -> int
        """
        为玩家背包物品充能。

        Args:
            rf (int): 充能能量值。
            charge_inv (bool, optional): 是否为物品充能。 Defaults to True.
            charge_armor (bool, optional): 是否为护甲充能。 Defaults to True.
            charge_charger (bool, optional): 是否为充电器充能。 Defaults to True.

        Returns:
            int: 充能后的能量值。
        """
        new_items = {}  # type: dict[tuple[int, int], Item]
        if charge_inv:
            for slot, item in GetAllInventoryItems(
                self.player_id, get_userdata=True
            ).items():
                if item.userData is None or GetIOPower(item.userData or {}, -1, -1) == (
                    -1,
                    -1,
                ):
                    continue
                if "skybluetech:battery" in item.GetBasicInfo().tags:
                    if not charge_charger:
                        continue
                    overflow, input_rf, _ = ChargeItem(rf, item)
                    if input_rf <= 0:
                        continue
                    rf = overflow
                    new_items[(ItemPosType.INVENTORY, slot)] = item
                    if rf <= 0:
                        break
                else:
                    overflow, input_rf, _ = ChargeItem(rf, item)
                    if input_rf <= 0:
                        continue
                    rf = overflow
                    new_items[(ItemPosType.INVENTORY, slot)] = item
                    if rf <= 0:
                        break
        if charge_armor:
            for slot, item in GetArmorSlotItems(
                self.player_id, get_userdata=True
            ).items():
                if item.userData is None or GetIOPower(item.userData or {}, -1, -1) == (
                    -1,
                    -1,
                ):
                    continue
                overflow, input_rf, _ = ChargeItem(rf, item)
                if input_rf <= 0:
                    continue
                rf = overflow
                new_items[(ItemPosType.ARMOR, slot)] = item
                if rf <= 0:
                    break
        SetPlayerAllItems(self.player_id, new_items)
        return rf

    def on_tick(self):
        if not self._charging:
            return
        chargers = {}  # type: dict[int, Item]
        charge_inv_items = {}  # type: dict[int, Item]
        charge_armor_items = {}  # type: dict[int, Item]
        for slot, item in GetAllInventoryItems(
            self.player_id, get_userdata=True
        ).items():
            if item.userData is None or GetIOPower(item.userData or {}, -1, -1) == (
                -1,
                -1,
            ):
                continue
            if "skybluetech:battery" in item.GetBasicInfo().tags:
                if not CanChargeInventory(item):
                    continue
                if IsEnableCharge(item):
                    chargers[slot] = item
                else:
                    continue
            else:
                charge_inv_items[slot] = item
        for slot, item in GetArmorSlotItems(self.player_id, get_userdata=True).items():
            if item.userData is None or GetIOPower(item.userData or {}, -1, -1) == (
                -1,
                -1,
            ):
                continue
            charge_armor_items[slot] = item
        if not chargers or not (charge_armor_items or charge_inv_items):
            self._charging = False
            return
        charge_inv_items_list = list(charge_inv_items.items())
        charge_armor_items_list = list(charge_armor_items.items())
        allitems = {}  # type: dict[tuple[int, int], Item]
        for charger_slot, charger_item in chargers.items():
            output_rf = GetIOPower(charger_item.userData or {})[1]
            total_rf, _ = GetCharge(charger_item.userData or {})
            if total_rf <= 0:
                continue
            charge_rf = charge_rf_origin = min(output_rf * 40, total_rf)  # 40t
            rf_rest = total_rf - charge_rf
            while charge_inv_items_list:
                slot, inv_item = charge_inv_items_list.pop(0)
                overflow, power_in, _ = ChargeItem(charge_rf, inv_item)
                if power_in <= 0:
                    continue
                charge_rf = overflow
                allitems[(ItemPosType.INVENTORY, slot)] = inv_item
                if charge_rf <= 0:
                    break
            while charge_armor_items_list:
                slot, armor_item = charge_armor_items_list.pop(0)
                overflow, power_in, _ = ChargeItem(charge_rf, armor_item)
                if power_in <= 0:
                    continue
                charge_rf = overflow
                allitems[(ItemPosType.ARMOR, slot)] = armor_item
                if charge_rf <= 0:
                    break
            rf_rest += charge_rf
            if charge_rf != charge_rf_origin:
                UpdateCharge(charger_item, rf_rest)
                allitems[(ItemPosType.INVENTORY, charger_slot)] = charger_item
        SetPlayerAllItems(self.player_id, allitems)

    @PlayerService.Listen(InventoryItemChangedServerEvent.WithUserData())
    def on_get_item(self, event):
        # type: (InventoryItemChangedServerEvent) -> None
        if event.playerId != self.player_id:
            return
        if GetIOPower(event.newItem.userData or {}, -1, -1) == (
            -1,
            -1,
        ):
            return
        self.enable_charge()
