# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.events.server import FarmBlockToDirtBlockServerEvent
from skybluetech_scripts.tooldelta.api.server import (
    SetBlock,
    GetPlayersInDim,
    GetPos,
    GetPlayerItem,
)
from ....common.define.id_enum import SKYBLUE_BOOTS, ObjectUpgraders
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
    for player_id in GetPlayersInDim(event.dimension):
        x, y, z = GetPos(player_id)
        if abs(x - event.x) < 1 and abs(y - event.y) < 2 and abs(z - event.z) < 1:
            target_id = player_id
            break
    if target_id is None:
        return
    slotitem = GetPlayerItem(target_id, SLOT_ARMOR, 3)
    if slotitem is None or slotitem.id != SKYBLUE_BOOTS:
        return
    upgraders = GetUpgraders(slotitem)
    if ObjectUpgraders.SPEC_NOFARM not in upgraders:
        return
    SetBlock(event.dimension, (event.x, event.y, event.z), "minecraft:farmland")
