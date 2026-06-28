# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import GetItemBasicInfo, SetItemLayer
from skybluetech_scripts.tooldelta.utils import nbt
from .lore import GetLorePos, SetLoreAtPos, SetLoreAuto

if 0:
    import typing

K_STORE_RF = "store_rf"
K_STORE_RF_MAX = "store_rf_max"
K_MAX_INPUT_POWER = "max_input_power"
K_MAX_OUTPUT_POWER = "max_output_power"
K_CHARGE_COST = "st:cost_rf"

ENERGY_BAR_LAYER = 1
ENERGY_BAR_LEVELS = 15


update_charge_callbacks = {}  # type: dict[str, typing.Callable[[Item, int], None]]


def UpdateCharge(item, store_rf, preserve_durability=False):
    # type: (Item, int, bool) -> None
    """
    强制更新物品的充能值。

    Args:
        item (Item): 物品
        store_rf (int): 物品的充能值
        preserve_durability (bool, optional): 是否不更新剩余能量的叠加贴图显示. Defaults to False.
    """
    ud = item.userData
    if ud is None:
        return
    ud[K_STORE_RF]["__value__"] = store_rf
    lore = "§r§e⚡ §b已储能 §a%d / %d RF" % (
        nbt.GetValueWithDefault(ud, K_STORE_RF, 0),
        nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1),
    )
    SetLoreAtPos(ud, GetLorePos(ud, "charge"), lore)
    cb = update_charge_callbacks.get(item.id)
    if cb is not None:
        cb(item, store_rf)
    if not preserve_durability:
        store_rf_max = nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1)
        level = int(float(store_rf) / store_rf_max * (ENERGY_BAR_LEVELS - 1))
        level = max(0, min(ENERGY_BAR_LEVELS - 1, level))
        SetItemLayer(item, ENERGY_BAR_LAYER, "skybluetech:energy_bar_%d" % level)
        # 能量改用叠加贴图显示, 清除残留的耐久损耗, 避免耐久条与叠加贴图同时表示能量。
        max_durability = item.GetBasicInfo().maxDurability
        if max_durability > 0:
            item.durability = max_durability
            damage = ud.get("Damage")
            if damage is not None:
                damage["__value__"] = 0


def UpdateChargeNBT(item_id, ud, store_rf):
    # type: (str, dict, int) -> None
    """
    更新物品的充能值 nbt。

    Args:
        item_id (str): 物品 id
        ud (dict): 物品 nbt
        store_rf (int): 物品的充能值
    """
    ud[K_STORE_RF]["__value__"] = store_rf
    lore = "§r§e⚡ §b已储能 §a%d / %d RF" % (
        nbt.GetValueWithDefault(ud, K_STORE_RF, 0),
        nbt.GetValueWithDefault(ud, K_STORE_RF_MAX, 1),
    )
    SetLoreAtPos(ud, GetLorePos(ud, "charge"), lore)
    # 能量改用叠加贴图显示, 此处无 Item 对象无法设置叠加贴图,
    # 但仍需清除残留的耐久损耗, 避免耐久条继续表示能量。
    if GetItemBasicInfo(item_id).maxDurability > 0:
        ud["Damage"] = nbt.Int(0)


def CanChargeInventory(item):
    # type: (Item) -> bool
    """
    检查物品是否可为物品栏物品进行充能

    Args:
        item (Item): 物品

    Returns:
        bool: 是否可为物品栏物品进行充能
    """
    ud = item.userData
    if ud is None:
        return False
    return nbt.GetValueWithDefault(ud, "can_charge_inventory", False)


def GetCharge(item_userdata):
    # type: (dict) -> tuple[int, int]
    """
    获取物品的充能值和最大充能值

    Args:
        item_userdata (dict): 物品 nbt

    Returns:
        tuple[int, int]: 充能值, 最大充能值
    """
    return nbt.GetValueWithDefault(
        item_userdata, K_STORE_RF, 0
    ), nbt.GetValueWithDefault(item_userdata, K_STORE_RF_MAX, 1)


def GetIOPower(item_userdata, default_input_power=0, default_output_power=0):
    # type: (dict, int, int) -> tuple[int, int]
    """
    获取可充能物品的充能最大输入输出功率

    Args:
        item_userdata (dict): 物品 nbt
        default_input_power (int, optional): 默认输入功率. Defaults to 0.
        default_output_power (int, optional): 默认输出功率. Defaults to 0.

    Returns:
        tuple[int, int]: 输入功率, 输出功率
    """
    return nbt.GetValueWithDefault(
        item_userdata, K_MAX_INPUT_POWER, default_input_power
    ), nbt.GetValueWithDefault(item_userdata, K_MAX_OUTPUT_POWER, default_output_power)


def GetPowerCost(item_userdata):
    # type: (dict) -> int
    """
    获取物品的单次能量消耗

    Args:
        item_userdata (dict): 物品 nbt

    Returns:
        int: 单次能量消耗
    """
    return nbt.GetValueWithDefault(item_userdata, K_CHARGE_COST, 0)


def IsEnableCharge(item):
    # type: (Item) -> bool
    """
    检查物品是否已启用充能。
    目前仅可检测电池是否可以对物品栏充能。

    Args:
        item (Item): 物品

    Returns:
        bool: 是否已启用充能
    """
    ud = item.userData
    if ud is None:
        return False
    return nbt.GetValueWithDefault(ud, "enable_charge", False)


def SetEnableCharge(item, enable):
    # type: (Item, bool) -> None
    """
    设置物品是否已启用充能。
    目前仅可设置电池是否可以对物品栏充能。

    Args:
        item (Item): 物品
        enable (bool): 是否启用充能
    """
    ud = item.userData
    if ud is None:
        return
    SetLoreAuto(
        ud, "charge_inventory", "§r§e◆ 便捷充能： " + ("§a启用" if enable else "§c禁用")
    )
    ud["enable_charge"] = nbt.Byte(enable)


def ChargeEnough(item_userdata):
    # type: (dict) -> bool
    """
    检查物品是否有足够的单次消耗能量

    Args:
        item_userdata (dict): 物品 nbt

    Returns:
        bool: 是否有足够的单次消耗能量
    """
    return GetCharge(item_userdata)[0] >= GetPowerCost(item_userdata)


def SetUpdateChargeCallback(item_id, callback):
    # type: (str, typing.Callable[[Item, int], None]) -> None
    "NOTE: INTERNAL USE"
    update_charge_callbacks[item_id] = callback


def ChargeItem(rf, item, times=1.0, preserve_durability=False):
    # type: (int, Item, float, bool) -> tuple[int, int, int]
    """
    为物品充能, 返回溢出的能量, 充入的能量和物品当前能量

    Args:
        rf (int): 输入的能量
        item (Item): 物品
        times (float, optional): 充能倍率. Defaults to 1.0.
        preserve_durability (bool, optional): 是否不改变现有耐久值. Defaults to False.

    Returns:
        tuple[int, int, int]: 溢出的能量, 充入的能量, 物品当前能量
    """
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
    UpdateCharge(item, item_rf + charge_in, preserve_durability=preserve_durability)
    return power_in_overflow + charge_in_overflow, charge_in, item_rf + charge_in
