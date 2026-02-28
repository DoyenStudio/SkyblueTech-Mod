# coding=utf-8
from mod.server import extraServerApi as serverApi
from skybluetech_scripts.tooldelta.define import Item
from ..actions.register import orig_tier_speed
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel, GetUpgraders, RemoveEnchant

EnchantType = serverApi.GetMinecraftEnum().EnchantType


ID = "skybluetech:obj_upgrader_fortune"


def onUpgrade(item, item_ud, up_ud):
    # type: (Item, dict, dict) -> None
    enchs = item.enchantData
    if enchs is None:
        enchs = item.enchantData = []
    for ench, lv in enchs:
        if ench == EnchantType.MiningLoot:
            return
    enchs.append((EnchantType.MiningLoot, GetUpgraderLevel(up_ud)))


def onReset(item, item_ud):
    # type: (Item, dict) -> None
    RemoveEnchant(item, EnchantType.MiningLoot)


RegisterUpdateCallback(ID, onUpgrade, onReset)
