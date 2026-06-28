# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import (
    SetItemTierSpeed,
    SetAttackDamage,
)
from skybluetech_scripts.tooldelta.utils import nbt

USELESS_SUFFIX = "_useless"
K_USELESS = "st:useless"
K_ORIGIN_ITEM_ID = "st:origin_item_id"
K_ORIGIN_TIER_SPEED = "st:origin_tier_speed"
K_ORIGIN_DAMAGE = "st:origin_damage"


def GetUselessItemId(item_id):
    # type: (str) -> str
    if item_id.endswith(USELESS_SUFFIX):
        return item_id
    return item_id + USELESS_SUFFIX


def GetOriginItemId(item_id):
    # type: (str) -> str
    if item_id.endswith(USELESS_SUFFIX):
        return item_id[: -len(USELESS_SUFFIX)]
    return item_id


def MakeItemUseless(item):
    # type: (Item) -> bool
    """
    使可充能物品转为 _useless 形态(切换 identifier 并写入耗尽标记)。
    工具、护甲等能量耗尽后均可复用。

    Args:
        item (Item): 所给物品

    Returns:
        bool: 是否在本次调用中新切换为耗尽形态(此前已是耗尽形态则返回 False)
    """
    ud = item.userData
    if ud is not None and ud.get(K_USELESS):
        item.newItemName = GetUselessItemId(item.id)
        return False
    origin_item_id = GetOriginItemId(item.id)
    if ud is None:
        ud = {}
    ud[K_ORIGIN_ITEM_ID] = nbt.String(origin_item_id)
    ud[K_USELESS] = True
    # _useless 物品无耐久概念: 清除继承自原物品的耐久值与损伤标记, 避免残留耐久条。
    ud.pop("Damage", None)
    item.userData = ud
    item.durability = None
    item._orig.pop("durability", None)
    item.newItemName = GetUselessItemId(origin_item_id)
    return True


def RecoverItemFromUseless(item):
    # type: (Item) -> None
    """
    将 _useless 物品恢复为原始 identifier 并清除耗尽标记。

    Args:
        item (Item): 所给物品
    """
    ud = item.userData
    if ud is None:
        return
    origin_item_id = nbt.GetValueWithDefault(ud, K_ORIGIN_ITEM_ID, None)
    if origin_item_id is None:
        origin_item_id = GetOriginItemId(item.id)
    item.newItemName = origin_item_id
    ud.pop(K_ORIGIN_ITEM_ID, None)
    ud.pop(K_USELESS, None)
    item.userData = ud


def MakeToolUseless(tool_item):
    # type: (Item) -> None
    """
    使得道具物品无法使用(在耗尽形态基础上额外清零挖掘速度与攻击力)。

    Args:
        tool_item (Item): 所给道具
    """
    ud = tool_item.userData
    if ud is None:
        origin_tier_speed = -1
        origin_damage = -1
    else:
        origin_tier_speed = nbt.GetValueWithDefault(ud, "ModTierSpeed", -1)
        origin_damage = nbt.GetValueWithDefault(ud, "ModAttackDamage", -1)
    if not MakeItemUseless(tool_item):
        return
    ud = tool_item.userData or {}
    ud[K_ORIGIN_TIER_SPEED] = nbt.Float(origin_tier_speed)
    ud[K_ORIGIN_DAMAGE] = nbt.Int(origin_damage)
    if not SetItemTierSpeed(tool_item, 0.0):
        print("[Error] failed to set item tier speed")
    if not SetAttackDamage(tool_item, 0):
        print("[Error] failed to set attack damage")


def RecoverToolFromUseless(tool_item):
    # type: (Item) -> None
    """
    恢复道具物品的原始属性(identifier、挖掘速度与攻击力)。

    Args:
        tool_item (Item): 所给道具
    """
    ud = tool_item.userData
    if ud is None:
        return
    origin_tier_speed = nbt.GetValueWithDefault(ud, K_ORIGIN_TIER_SPEED, None)
    origin_damage = nbt.GetValueWithDefault(ud, K_ORIGIN_DAMAGE, None)
    RecoverItemFromUseless(tool_item)
    ud = tool_item.userData
    if ud is None:
        return
    if origin_tier_speed == 0:
        origin_tier_speed = -1
    if origin_damage == 0:
        origin_damage = -1
    if origin_tier_speed == -1:
        ud.pop("ModTierSpeed", None)
    elif origin_tier_speed is not None:
        SetItemTierSpeed(tool_item, origin_tier_speed)
    if origin_damage == -1:
        ud.pop("ModAttackDamage", None)
    elif origin_damage is not None:
        SetAttackDamage(tool_item, origin_damage)
    ud = tool_item.userData or ud
    ud.pop(K_ORIGIN_TIER_SPEED, None)
    ud.pop(K_ORIGIN_DAMAGE, None)
    tool_item.userData = ud
