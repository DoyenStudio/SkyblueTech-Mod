# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    DestroyEntity,
    GetPlayerMainhandItem,
    GetEntitiesInSquareArea,
    GetDroppedItem,
    GetPos,
    SetCommand,
    SetMotion,
    SpawnDroppedItem,
    SpawnItemToPlayerCarried,
)
from skybluetech_scripts.tooldelta.events.server import StartDestroyBlockServerEvent
from ...common.define.facing import FACING_DXYZ
from ...common.define.id_enum.items import METAL_HAMMER
from ...common.tools_def.metal_hammer import recipes


@StartDestroyBlockServerEvent.Listen()
def onStartDestroyBlock(event):
    # type: (StartDestroyBlockServerEvent) -> None
    mhitem = GetPlayerMainhandItem(event.playerId)
    if mhitem is None or mhitem.id != METAL_HAMMER or mhitem.durability is None:
        return
    x, y, z = (int(i) for i in event.pos)
    dx, dy, dz = FACING_DXYZ[event.face]
    entities = GetEntitiesInSquareArea(
        None,
        (x + dx, y + dy, z + dz),
        (x + dx + 1, y + dy + 1, z + dz + 1),
        event.dimensionId,
    )
    if not entities:
        return
    event.cancel()
    for entity_id in entities:
        pos = GetPos(entity_id)
        item = GetDroppedItem(entity_id)
        if item is None:
            continue
        rcp = recipes.recipes_mapping.get(item.id)
        if rcp is None:
            continue
        item.count -= 1
        mhitem.durability -= 1
        # todo: 添加粒子特效
        SetCommand("playsound random.anvil_land @a", entity_id)
        DestroyEntity(entity_id)
        if item.count > 0:
            dp_entity_id = SpawnDroppedItem(event.dimensionId, pos, item)
            if dp_entity_id is not None:
                SetMotion(dp_entity_id, (0, 0, 0))
        dp_entity_id = SpawnDroppedItem(event.dimensionId, pos, Item(rcp.hammer_out))
        if dp_entity_id is not None:
            SetMotion(dp_entity_id, (0, 0, 0))
        if mhitem.durability <= 0:
            SpawnItemToPlayerCarried(event.playerId, Item("minecraft:air"))
            SetCommand("playsound random.break", event.playerId)
        else:
            SpawnItemToPlayerCarried(event.playerId, mhitem)
        return
