# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from collections import deque
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import DestroyBlockEvent

from skybluetech_scripts.skybluetech.common.define.id_enum import ObjectUpgraders
from skybluetech_scripts.skybluetech.common.machinery_def.redstone_furnace import (
    TICK_POWER,
)
from ...machinery.redstone_furnace import get_furnace_output_by_input
from ...machinery.utils.charge import GetCharge, UpdateCharge
from .register import RegisterDestroyBlockCallback

BURN_POWER_SINGLE = TICK_POWER * 20


def onAutoBurn(event, use_tool, item_ud, upgrader_ud):
    # type: (DestroyBlockEvent, Item, dict, dict) -> None
    charge, _ = GetCharge(item_ud)
    for item_eid in event.dropEntityIds:
        it = CF.CreateItem(LEVEL_ID).GetDroppedItem(item_eid, False)
        it = Item.from_dict(it) if it is not None else None
        if it is None:
            continue
        res = get_furnace_output_by_input(it.id)
        if res is None:
            continue
        if charge < BURN_POWER_SINGLE:
            break
        charge -= BURN_POWER_SINGLE
        GetServer().DestroyEntity(item_eid)
        GetServer().CreateEngineItemEntity(Item(res, count=it.count).marshal(), event.dimensionId, (event.x + 0.5, event.y + 0.5, event.z + 0.5))
    UpdateCharge(use_tool, charge)
    CF.CreateItem(event.playerId).SpawnItemToPlayerCarried(use_tool.marshal(), event.playerId)


RegisterDestroyBlockCallback(ObjectUpgraders.AUTO_BURNING, onAutoBurn)
