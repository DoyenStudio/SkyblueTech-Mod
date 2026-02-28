# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils import nbt
from ..actions.register import orig_tier_speed
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel

ID = "skybluetech:obj_upgrader_digspeed"


def onUpgrade(item, item_ud, up_ud):
    # type: (Item, dict, dict) -> None
    if item.id not in orig_tier_speed:
        return
    item_ud["ModTierSpeed"] = nbt.Float(
        orig_tier_speed[item.id] + round(3 * 1.5 ** GetUpgraderLevel(up_ud), 2)
    )


def onReset(item, item_ud):
    # type: (Item, dict) -> None
    if item.id not in orig_tier_speed:
        return
    item_ud["ModTierSpeed"] = nbt.Float(orig_tier_speed[item.id])


RegisterUpdateCallback(ID, onUpgrade, onReset)
