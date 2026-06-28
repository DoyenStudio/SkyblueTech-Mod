# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import ItemExists, SetPlayerAllItems
from skybluetech_scripts.tooldelta.utils import nbt

GLASS_TUBE_TAG = "skybluetech:glass_tube"
"玻璃试管物品 tag"
GLASS_TUBE_MAX_VOLUME = 500.0
"玻璃试管最大可存流体容积 (mB)"

# TODO: 应在流体枚举处编写一个无法用试管提取的流体的枚举类

K_GT_FLUID_ID = "gt_fluid_id"
"玻璃试管 userData 中存储的流体 ID"
K_GT_VOLUME = "gt_volume"
"玻璃试管 userData 中存储的流体体积"

_ItemPosType = GetMinecraftEnum().ItemPosType


def IsGlassTube(item):
    # type: (Item) -> bool
    "物品是否为玻璃试管。"
    if item is None:
        return False
    return GLASS_TUBE_TAG in item.GetBasicInfo().tags


def GetTubeContent(item):
    # type: (Item) -> tuple[str | None, float]
    """
    读取玻璃试管内存储的流体。

    Returns:
        tuple[str | None, float]: 流体 ID (空试管为 None), 流体体积
    """
    ud = item.userData
    if not ud:
        return None, 0.0
    fluid_id = nbt.GetValueWithDefault(ud, K_GT_FLUID_ID, None)
    volume = nbt.GetValueWithDefault(ud, K_GT_VOLUME, 0.0) or 0.0
    if not fluid_id or volume <= 0:
        return None, 0.0
    return fluid_id, volume


def ApplyTubeContent(player_id, item, fluid_id, volume):
    # type: (str, Item, str | None, float) -> None
    """
    将流体内容写回玻璃试管物品的 userData, 并刷新玩家手持物品。
    """
    ud = item.userData or {}
    if not fluid_id or volume <= 0:
        ud[K_GT_FLUID_ID] = nbt.String("")
        ud[K_GT_VOLUME] = nbt.Float(0.0)
        lore = "§r§7空 §80 / %d mB" % int(GLASS_TUBE_MAX_VOLUME)
    else:
        ud[K_GT_FLUID_ID] = nbt.String(fluid_id)
        ud[K_GT_VOLUME] = nbt.Float(volume)
        lore = "§r§b%s §a%d §7/ %d mB" % (
            _GetFluidName(fluid_id),
            int(round(volume)),
            int(GLASS_TUBE_MAX_VOLUME),
        )
    ud["display"] = {"Lore": [nbt.String(lore)]}
    item.userData = ud
    SetPlayerAllItems(player_id, {(_ItemPosType.CARRIED, 0): item})


def _GetFluidName(fluid_id):
    # type: (str) -> str
    if ItemExists(fluid_id):
        return Item(fluid_id).GetBasicInfo().itemName
    return fluid_id
