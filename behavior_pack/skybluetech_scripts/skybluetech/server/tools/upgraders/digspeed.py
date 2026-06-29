# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils import nbt
from skybluetech_scripts.skybluetech.common.define.id_enum import ObjectUpgraders
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel

_BASE_SPEED = 16.0


def onUpgrade(item, item_ud, up_ud):
    # type: (Item, dict, dict) -> None
    item_ud["ModTierSpeed"] = nbt.Float(
        _BASE_SPEED + round(6 * GetUpgraderLevel(up_ud), 2)
    )


def onReset(item, item_ud):
    # type: (Item, dict) -> None
    item_ud["ModTierSpeed"] = nbt.Float(_BASE_SPEED)


RegisterUpdateCallback(ObjectUpgraders.DIGSPEED, onUpgrade, onReset)
