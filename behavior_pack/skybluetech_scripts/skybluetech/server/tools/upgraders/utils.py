# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault

def GetUpgraders(item):
    # type: (Item) -> dict
    ud = item.userData
    if ud is None:
        return {}
    return ud.get("st:upgraders", {})

def GetUpgraderLevel(upgrade_data):
    # type: (dict) -> int
    return upgrade_data["st:level"]["__value__"]

def RemoveEnchant(upgrade_item, enchant_id):
    # type: (Item, int) -> None
    if upgrade_item.enchantData is not None:
        for enc, _ in upgrade_item.enchantData[:]:
            if enc == enchant_id:
                upgrade_item.enchantData.remove((enc, _))
    if upgrade_item.userData is not None:
        for enchant in upgrade_item.userData.get("ench", []):
            if GetValueWithDefault(enchant, "id", 0) == enchant_id:
                upgrade_item.userData["ench"].remove(enchant)
                break
        if "ench" in upgrade_item.userData and not upgrade_item.userData["ench"]:
            del upgrade_item.userData["ench"]

