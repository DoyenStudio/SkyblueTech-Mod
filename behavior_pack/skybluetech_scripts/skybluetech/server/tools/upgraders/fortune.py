# coding=utf-8
from mod.server import extraServerApi as serverApi
from skybluetech_scripts.tooldelta.define import Item
from ....common.define.id_enum.items import ObjectUpgraders
from .register import RegisterUpdateCallback
from .utils import GetUpgraderLevel, RemoveEnchant

EnchantType = serverApi.GetMinecraftEnum().EnchantType


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


RegisterUpdateCallback(ObjectUpgraders.FORTUNE, onUpgrade, onReset)
