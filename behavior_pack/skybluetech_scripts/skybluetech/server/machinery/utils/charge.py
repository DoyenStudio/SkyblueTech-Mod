# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.utils import nbt
from .lore import GetLorePos, SetLoreAtPos

if 0:
    from typing import Callable

K_STORE_RF = "store_rf"
K_STORE_RF_MAX = "store_rf_max"
K_CHARGE_COST = "st:cost_rf"


def g(dic, key):
    return dic[key]["__value__"]


update_charge_callbacks = {}  # type: dict[str, Callable[[str, Item, int], None]]


def UpdateCharge(owner, item, store_rf):
    # type: (str, Item, int) -> None
    ud = item.userData
    if ud is None:
        return
    ud[K_STORE_RF]["__value__"] = store_rf
    lore = "§r§e⚡ §b已储能 §a%d / %d RF" % (g(ud, K_STORE_RF), g(ud, K_STORE_RF_MAX))
    SetLoreAtPos(ud, GetLorePos(ud, "charge"), lore)
    max_durability = item.GetBasicInfo().maxDurability
    if max_durability > 0:
        if ud is None:
            ud = item.userData = {}
        item.durability = max(
            2, int(float(store_rf) / g(ud, K_STORE_RF_MAX) * max_durability)
        )
        ud.setdefault("Damage", nbt.Int(0))["__value__"] = (
            max_durability - item.durability
        )
    cb = update_charge_callbacks.get(item.id)
    if cb is not None:
        cb(owner, item, store_rf)


def GetCharge(item_userdata):
    # type: (dict) -> tuple[int, int]
    return g(item_userdata, K_STORE_RF), g(item_userdata, K_STORE_RF_MAX)


def GetChargeCost(item_userdata):
    # type: (dict) -> int
    return g(item_userdata, K_CHARGE_COST)


def ChargeEnough(item_userdata):
    # type: (dict) -> bool
    return GetCharge(item_userdata)[0] >= GetChargeCost(item_userdata)


def SetUpdateChargeCallback(item_id, callback):
    # type: (str, Callable[[str, Item, int], None]) -> None
    update_charge_callbacks[item_id] = callback
