# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ServerItemUseOnEvent
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetBlockStates,
    SetBlock,
    SpawnItemToPlayerCarried,
)
from ....common.machinery_def.farming_station import isRipedCrop
from ...machinery.utils.charge import GetCharge, UpdateCharge
from .register import RegisterItemUseOnCallback
from .utils import GetUpgraderLevel

ID = "skybluetech:obj_upgrader_spec_farming"
POWER_COST = 2000

DIRTLIKE_BLOCK = {"minecraft:dirt", "minecraft:grass_block"}
HOE_POWER_COST = 200


def getCropsRiped(dim, _x, _y, _z, radius):
    # type: (int, int, int, int, int) -> list[tuple[int, int, int, int, str]]
    res = []  # type: list[tuple[int, int, int, int, str]]
    for x in range(_x - radius, _x + radius + 1):
        for z in range(_z - radius, _z + radius + 1):
            block_id = GetBlockName(dim, (x, _y, z))
            if block_id is None:
                continue
            block_states = GetBlockStates(dim, (x, _y, z))
            if block_states is None:
                continue
            if isRipedCrop(block_id, block_states):
                res.append((dim, x, _y, z, block_id))
    return res


def onHarvest(event, item_ud, upgrader_ud):
    # type: (ServerItemUseOnEvent, dict, dict) -> None
    item = event.item
    r = GetUpgraderLevel(upgrader_ud)
    if event.blockName in DIRTLIKE_BLOCK:
        charge, _ = GetCharge(item_ud)
        if charge < HOE_POWER_COST:
            event.cancel()
            return
    else:
        crops_riped = getCropsRiped(event.dimensionId, event.x, event.y, event.z, r)
        if not crops_riped:
            return
        charge, _ = GetCharge(item_ud)
        if charge < POWER_COST:
            return
        charge -= POWER_COST
        for dim, x, y, z, block_id in crops_riped:
            SetBlock(dim, (x, y, z), block_id, aux_value=0, old_block_handing=1)
        UpdateCharge(event.entityId, item, charge)
        SpawnItemToPlayerCarried(event.entityId, item)


RegisterItemUseOnCallback(ID, onHarvest)
