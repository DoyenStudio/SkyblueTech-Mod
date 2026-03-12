# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import GetItemBasicInfo
from skybluetech_scripts.tooldelta.utils import nbt
from .lore import GetLorePos, SetLoreAtPos

if 0:
    from typing import Callable

K_STORE_RF = "store_rf"
K_STORE_RF_MAX = "store_rf_max"
K_MAX_OUTPUT_POWER = "max_output_power"
K_CHARGE_COST = "st:cost_rf"


update_charge_callbacks = {}  # type: dict[str, Callable[[str, Item, int], None]]


def UpdateCharge(owner, item, store_rf):
    # type: (str, Item, int) -> None
    ud = item.userData
    if ud is None:
        return
    ud[K_STORE_RF]["__value__"] = store_rf
    lore = "§r§e⚡ §b已储能 §a%d / %d RF" % (
        nbt.GetValueWithDefault(ud, K_STORE_RF, 0),
        nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1),
    )
    SetLoreAtPos(ud, GetLorePos(ud, "charge"), lore)
    max_durability = item.GetBasicInfo().maxDurability
    if max_durability > 0:
        if ud is None:
            ud = item.userData = {}
        store_rf_max = nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1)
        item.durability = max(
            2,
            int(float(store_rf) / store_rf_max * max_durability),
        )
        ud.setdefault("Damage", nbt.Int(0))["__value__"] = (
            max_durability - item.durability
        )
    cb = update_charge_callbacks.get(item.id)
    if cb is not None:
        cb(owner, item, store_rf)


def UpdateChargeNBT(item_id, ud, store_rf):
    # type: (str, dict, int) -> None
    ud[K_STORE_RF]["__value__"] = store_rf
    lore = "§r§e⚡ §b已储能 §a%d / %d RF" % (
        nbt.GetValueWithDefault(ud, K_STORE_RF, 0),
        nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1),
    )
    SetLoreAtPos(ud, GetLorePos(ud, "charge"), lore)
    max_durability = GetItemBasicInfo(item_id).maxDurability
    store_rf_max = nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1)
    if max_durability > 0:
        ud["Damage"] = nbt.Int(
            max(
                2,
                int(1 - float(store_rf) / store_rf_max),
            )
        )


def GetCharge(item_userdata):
    # type: (dict) -> tuple[int, int]
    return nbt.GetValueWithDefault(
        item_userdata, K_STORE_RF, 0
    ), nbt.GetValueWithDefault(item_userdata, K_STORE_RF_MAX, 1)


def GetOutputPower(item_userdata):
    # type: (dict) -> int
    return nbt.GetValueWithDefault(item_userdata, K_MAX_OUTPUT_POWER, 0)


def GetChargeCost(item_userdata):
    # type: (dict) -> int
    return nbt.GetValueWithDefault(item_userdata, K_CHARGE_COST, 0)


def ChargeEnough(item_userdata):
    # type: (dict) -> bool
    return GetCharge(item_userdata)[0] >= GetChargeCost(item_userdata)


def SetUpdateChargeCallback(item_id, callback):
    # type: (str, Callable[[str, Item, int], None]) -> None
    update_charge_callbacks[item_id] = callback
