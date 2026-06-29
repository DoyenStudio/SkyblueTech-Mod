# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils import nbt
from skybluetech_scripts.skybluetech.common.define.id_enum import ObjectUpgraders
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel


def _get_base_damage(item):
    # type: (Item) -> int
    base = item.GetBasicInfo().weaponDamage
    return base if base > 0 else 8


def onUpgrade(item, item_ud, up_ud):
    # type: (Item, dict, dict) -> None
    item_ud["ModAttackDamage"] = nbt.Int(
        _get_base_damage(item) + int(3 * 1.5 ** GetUpgraderLevel(up_ud))
    )


def onReset(item, item_ud):
    # type: (Item, dict) -> None
    item_ud["ModAttackDamage"] = nbt.Int(_get_base_damage(item))


RegisterUpdateCallback(ObjectUpgraders.ATTACK, onUpgrade, onReset)
