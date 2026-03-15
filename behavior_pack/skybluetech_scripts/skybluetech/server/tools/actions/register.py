# coding=utf-8
#
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    ServerItemTryUseEvent,
    ServerItemUseOnEvent,
)
from skybluetech_scripts.tooldelta.api.server.item import (
    SetItemTierSpeed,
    SetAttackDamage,
)
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from ...machinery.utils.charge import ChargeEnough, SetUpdateChargeCallback

# TYPE_CHECKING
if 0:
    from typing import Callable
# TYPE_CHECKING END

item_pre_use_cbs = {}  # type: dict[str, Callable[[ServerItemTryUseEvent]]]
item_pre_use_on_block_cbs = {}  # type: dict[str, Callable[[ServerItemUseOnEvent]]]
tool_items = set()  # type: set[str]
orig_tier_speed = {}  # type: dict[str, float]
orig_attack_damage = {}  # type: dict[str, int]


def RegisterTool(item_id):
    # type: (str) -> None
    "注册工具, 使得工具能在耐久变动缺乏能量后无法挖掘方块。"
    tool_items.add(item_id)


def RegisterItemPreUseCallback(item_id, callback):
    # type: (str, Callable[[ServerItemTryUseEvent]]) -> None
    "注册物品的预使用回调。"
    item_pre_use_cbs[item_id] = callback


def RegisterItemPreUseOnBlockCallback(item_id, callback):
    # type: (str, Callable[[ServerItemUseOnEvent]]) -> None
    "注册物品对方块的预使用回调。"
    item_pre_use_on_block_cbs[item_id] = callback


def SetOriginTierSpeed(item_id, tier_speed):
    # type: (str, float) -> None
    "设置工具的原始 TierSpeed 值。"

    def regfunc(item, charge):
        # type: (Item, int) -> None
        ud = item.userData
        if ud is None:
            return
        if ChargeEnough(ud) and GetValueWithDefault(ud, "ModTierSpeed", 0.0) == 0.0:
            SetItemTierSpeed(item, tier_speed)

    orig_tier_speed[item_id] = tier_speed
    SetUpdateChargeCallback(item_id, regfunc)


def SetOriginAttackDamage(item_id, attack_damage):
    # type: (str, int) -> None
    "设置工具的原始 AttackDamage 值。"

    def regfunc(item, charge):
        # type: (Item, int) -> None
        ud = item.userData
        if ud is None:
            return
        if ChargeEnough(ud) and GetValueWithDefault(ud, "ModAttackDamage", 0.0) == 0.0:
            SetAttackDamage(item, attack_damage)

    orig_attack_damage[item_id] = attack_damage
    SetUpdateChargeCallback(item_id, regfunc)
