# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import DestroyBlockEvent
from skybluetech_scripts.tooldelta.api.server import (
    SpawnItemToPlayerCarried,
    GetDroppedItem,
    DestroyEntity,
    SpawnDroppedItem,
)
from ....common.define.id_enum import ObjectUpgraders
from ....common.machinery_def.redstone_furnace import TICK_POWER
from ...machinery.redstone_furnace import get_furnace_output_by_input
from ...machinery.utils.charge import GetCharge, UpdateCharge
from .register import RegisterDestroyBlockCallback

BURN_POWER_SINGLE = TICK_POWER * 20 * 10


def onAutoBurn(event, use_tool, item_ud, upgrader_ud):
    # type: (DestroyBlockEvent, Item, dict, dict) -> None
    charge, _ = GetCharge(item_ud)
    for item_eid in event.dropEntityIds:
        it = GetDroppedItem(item_eid)
        if it is None:
            continue
        res = get_furnace_output_by_input(it.id)
        if res is None:
            continue
        if charge < BURN_POWER_SINGLE:
            break
        charge -= BURN_POWER_SINGLE
        DestroyEntity(item_eid)
        SpawnDroppedItem(
            event.dimensionId,
            (event.x + 0.5, event.y + 0.5, event.z + 0.5),
            Item(res, count=it.count),
        )
    UpdateCharge(event.playerId, use_tool, charge)
    SpawnItemToPlayerCarried(event.playerId, use_tool)


RegisterDestroyBlockCallback(ObjectUpgraders.AUTO_BURNING, onAutoBurn)
