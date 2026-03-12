# coding=utf-8
from ..define import Item
from ..utils import nbt


# def ItemToNBT(item):
#     # type: (Item) -> dict
#     "TODO: 暂不支持附魔导出"
#     ret = {"Count": item.count}
#     if item.userData is not None:
#         ret["tag"] = item.userData
#     if item.durability is not None:
#         ret["Damage"] = item.GetBasicInfo().maxDurability - item.durability
#     return ret


# def NBTToItem(item_nbt):
#     # type: (dict) -> Item
#     "TODO: 只能导出部分物品数据"
#     item_id = nbt.GetValue(item_nbt, "Name")
#     damage = item_nbt.get("Damage")
#     if damage is not None:
#         durability = Item(item_id, 0).GetBasicInfo().maxDurability - nbt.GetValue(
#             item_nbt, "Damage"
#         )
#     else:
#         durability = None
#     return Item(
#         item_id,
#         0,
#         count=item_nbt["Count"],
#         userData=item_nbt.get("tag"),
#         durability=durability,
#     )


class INBTKey:
    ID = "id"
    AUX = "aux"
    COUNT = "count"
    SHOW_IN_HAND = "showInHand"
    ENCHANT_DATA = "enchantData"
    MOD_ENCHANT_DATA = "modEnchantData"
    CUSTOM_TIPS = "customTips"
    EXTRA_ID = "extraId"
    USER_DATA = "userData"
    DURABILITY = "durability"
    ENCHANT_ENCH = "ench"
    ENCHANT_LV = "lv"


def Item2INBT(item):
    # type: (Item) -> dict
    res = {
        INBTKey.ID: nbt.String(item.id),
        INBTKey.AUX: nbt.Int(item.newAuxValue),
        INBTKey.COUNT: nbt.Short(item.count),
        INBTKey.SHOW_IN_HAND: nbt.Byte(item.showInHand),
    }  # type: dict
    enchantData = item.enchantData
    if enchantData is not None:
        res[INBTKey.ENCHANT_DATA] = [
            {
                INBTKey.ENCHANT_ENCH: nbt.Short(ench),
                INBTKey.ENCHANT_LV: nbt.Short(level),
            }
            for ench, level in enchantData
        ]
    modEnchantData = item.modEnchantData
    if modEnchantData is not None:
        res[INBTKey.MOD_ENCHANT_DATA] = [
            {
                INBTKey.ENCHANT_ENCH: nbt.String(ench),
                INBTKey.ENCHANT_LV: nbt.Short(level),
            }
            for ench, level in modEnchantData
        ]
    customTips = item.customTips
    if customTips is not None:
        res[INBTKey.CUSTOM_TIPS] = nbt.String(customTips)
    extraId = item.extraId
    if extraId is not None:
        res[INBTKey.EXTRA_ID] = nbt.String(extraId)
    userData = item.userData
    if userData is not None:
        res[INBTKey.USER_DATA] = userData
    durability = item.durability
    if durability is not None:
        res[INBTKey.DURABILITY] = nbt.Int(durability)
    return res


def INBT2Item(inbt):
    # type: (dict) -> Item
    enchantData = inbt.get("enchantData", None)
    if enchantData is not None:
        enchantData = [
            (
                nbt.GetValue(ench, INBTKey.ENCHANT_ENCH),
                nbt.GetValue(ench, INBTKey.ENCHANT_LV),
            )
            for ench in enchantData
        ]
    modEnchantData = inbt.get("modEnchantData")
    if modEnchantData is not None:
        modEnchantData = [
            (
                nbt.GetValue(ench, INBTKey.ENCHANT_ENCH),
                nbt.GetValue(ench, INBTKey.ENCHANT_LV),
            )
            for ench in modEnchantData
        ]
    customTips = nbt.GetValueWithDefault(inbt, INBTKey.CUSTOM_TIPS, None)
    extraId = nbt.GetValueWithDefault(inbt, INBTKey.EXTRA_ID, None)
    userData = inbt.get(INBTKey.USER_DATA, None)
    durability = nbt.GetValueWithDefault(inbt, INBTKey.DURABILITY, None)
    return Item(
        newItemName=nbt.GetValue(inbt, INBTKey.ID),
        newAuxValue=nbt.GetValueWithDefault(inbt, INBTKey.AUX, 0),
        count=nbt.GetValueWithDefault(inbt, INBTKey.COUNT, 1),
        showInHand=nbt.GetValueWithDefault(inbt, INBTKey.SHOW_IN_HAND, True),
        extraId=extraId,
        enchantData=enchantData,
        modEnchantData=modEnchantData,
        customTips=customTips,
        userData=userData,
        durability=durability,
    )


def GetINBTItemId(inbt):
    # type: (dict) -> str
    return nbt.GetValue(inbt, "id")


def GetINBTItemAux(inbt):
    # type: (dict) -> int
    return nbt.GetValueWithDefault(inbt, "aux", 0)


def GetINBTUserData(inbt):
    # type: (dict) -> dict
    return nbt.GetValueWithDefault(inbt, "userData", None)
