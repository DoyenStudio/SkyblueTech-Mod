# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetPlayerList
from skybluetech_scripts.tooldelta.define import Item
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.events.server import FarmBlockToDirtBlockServerEvent

from skybluetech_scripts.skybluetech.common.define.id_enum import (
    SKYBLUE_BOOTS,
    ObjectUpgraders,
)
from .utils import GetUpgraders

ID = "skybluetech:obj_upgrader_spec_nofarm"
POWER_COST = 2000
SLOT_ARMOR = GetMinecraftEnum().ItemPosType.ARMOR


@FarmBlockToDirtBlockServerEvent.Listen()
def onFarmBlockToDirt(event):
    # type: (FarmBlockToDirtBlockServerEvent) -> None
    if not event.is_manual:
        return
    target_id = None
    for player_id in [player_id for player_id in GetPlayerList() if CF.CreateDimension(player_id).GetEntityDimensionId(
    ) == event.dimension]:
        x, y, z = CF.CreatePos(player_id).GetPos()
        if abs(x - event.x) < 1 and abs(y - event.y) < 2 and abs(z - event.z) < 1:
            target_id = player_id
            break
    if target_id is None:
        return
    slotitem = CF.CreateItem(target_id).GetPlayerItem(SLOT_ARMOR, 3, False)
    slotitem = Item.from_dict(slotitem) if slotitem is not None else None
    if slotitem is None or slotitem.id != SKYBLUE_BOOTS:
        return
    upgraders = GetUpgraders(slotitem)
    if ObjectUpgraders.SPEC_NOFARM not in upgraders:
        return
    CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
        (event.x, event.y, event.z),
        {"name": "minecraft:farmland", "aux": 0},
        0,
        dimensionId=event.dimension,
    )
