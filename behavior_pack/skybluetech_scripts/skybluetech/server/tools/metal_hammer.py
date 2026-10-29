# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item

from skybluetech_scripts.tooldelta.events.server import StartDestroyBlockServerEvent
from ...common.define.facing import FACING_DXYZ
from ...common.define.id_enum.items import METAL_HAMMER
from ...common.tools_def.metal_hammer import recipes


@StartDestroyBlockServerEvent.Listen()
def onStartDestroyBlock(event):
    # type: (StartDestroyBlockServerEvent) -> None
    mhitem = CF.CreateItem(event.playerId).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mhitem = Item.from_dict(mhitem) if mhitem is not None else None
    if mhitem is None or mhitem.id != METAL_HAMMER or mhitem.durability is None:
        return
    x, y, z = (int(i) for i in event.pos)
    dx, dy, dz = FACING_DXYZ[event.face]
    entities = CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(
        None,
        (x + dx, y + dy, z + dz),
        (x + dx + 1, y + dy + 1, z + dz + 1),
        event.dimensionId,
    )
    if not entities:
        return
    event.cancel()
    for entity_id in entities:
        pos = CF.CreatePos(entity_id).GetPos()
        item = CF.CreateItem(LEVEL_ID).GetDroppedItem(entity_id, False)
        item = Item.from_dict(item) if item is not None else None
        if item is None:
            continue
        rcp = recipes.recipes_mapping.get(item.id)
        if rcp is None:
            continue
        item.count -= 1
        mhitem.durability -= 1
        # todo: 添加粒子特效
        CF.CreateCommand(LEVEL_ID).SetCommand("playsound random.anvil_land @a[r=25]", entity_id)
        GetServer().DestroyEntity(entity_id)
        if item.count > 0:
            dp_entity_id = GetServer().CreateEngineItemEntity(item.marshal(), event.dimensionId, pos)
            if dp_entity_id is not None:
                CF.CreateActorMotion(dp_entity_id).SetMotion((0, 0, 0))
        dp_entity_id = GetServer().CreateEngineItemEntity(Item(rcp.hammer_out).marshal(), event.dimensionId, pos)
        if dp_entity_id is not None:
            CF.CreateActorMotion(dp_entity_id).SetMotion((0, 0, 0))
        if mhitem.durability <= 0:
            CF.CreateItem(event.playerId).SpawnItemToPlayerCarried(
                Item("minecraft:air").marshal(),
                event.playerId,
            )
            CF.CreateCommand(LEVEL_ID).SetCommand("playsound random.break", event.playerId)
        else:
            CF.CreateItem(event.playerId).SpawnItemToPlayerCarried(mhitem.marshal(), event.playerId)
        return
