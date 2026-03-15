# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import GetItemBasicInfo
from skybluetech_scripts.tooldelta.utils import nbt
from .lore import GetLorePos, SetLoreAtPos

if 0:
    from typing import Callable

K_STORE_RF = "store_rf"
K_STORE_RF_MAX = "store_rf_max"
K_MAX_INPUT_POWER = "max_input_power"
K_MAX_OUTPUT_POWER = "max_output_power"
K_CHARGE_COST = "st:cost_rf"


update_charge_callbacks = {}  # type: dict[str, Callable[[Item, int], None]]


def UpdateCharge(item, store_rf):
    # type: (Item, int) -> None
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
        cb(item, store_rf)


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


def GetIOPower(item_userdata, default_input_power=0, default_output_power=0):
    # type: (dict, int, int) -> tuple[int, int]
    return nbt.GetValueWithDefault(
        item_userdata, K_MAX_INPUT_POWER, default_input_power
    ), nbt.GetValueWithDefault(item_userdata, K_MAX_OUTPUT_POWER, default_output_power)


def GetChargeCost(item_userdata):
    # type: (dict) -> int
    return nbt.GetValueWithDefault(item_userdata, K_CHARGE_COST, 0)


def ChargeEnough(item_userdata):
    # type: (dict) -> bool
    return GetCharge(item_userdata)[0] >= GetChargeCost(item_userdata)


def SetUpdateChargeCallback(item_id, callback):
    # type: (str, Callable[[Item, int], None]) -> None
    update_charge_callbacks[item_id] = callback


def ChargeItem(rf, item, times=1.0):
    # type: (int, Item, float) -> tuple[int, int, int]
    "为物品充能, 返回溢出的能量, 充入的能量和物品当前能量"
    ud = item.userData
    if ud is None:
        return rf, 0, 0
    item_rf, item_rf_max = GetCharge(ud)
    input_power, _ = GetIOPower(ud)
    input_power = int(input_power * times)
    power_in = min(rf, item_rf_max - item_rf)
    power_in_overflow = rf - power_in
    charge_in = min(power_in, input_power)
    charge_in_overflow = power_in - charge_in
    UpdateCharge(item, item_rf + charge_in)
    return power_in_overflow + charge_in_overflow, charge_in, item_rf + charge_in
