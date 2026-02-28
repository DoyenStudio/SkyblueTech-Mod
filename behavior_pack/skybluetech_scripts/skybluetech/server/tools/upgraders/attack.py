# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils import nbt
from ..actions.register import orig_attack_damage
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel


ID = "skybluetech:obj_upgrader_attack"


def onUpgrade(item, item_ud, up_ud):
    # type: (Item, dict, dict) -> None
    if item.id not in orig_attack_damage:
        return
    item_ud["ModAttackDamage"] = nbt.Int(
        orig_attack_damage[item.id] + int(3 * 1.5 ** GetUpgraderLevel(up_ud))
    )


def onReset(item, item_ud):
    # type: (Item, dict) -> None
    if item.id not in orig_attack_damage:
        return
    item_ud["ModAttackDamage"] = nbt.Int(orig_attack_damage[item.id])


RegisterUpdateCallback(ID, onUpgrade, onReset)
