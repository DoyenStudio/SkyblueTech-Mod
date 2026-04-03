# coding=utf-8
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ...define.item import Item
from ...internal import GetServer
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

GetEntitiesInSquareArea = MethodCacher(
    lambda: CF.CreateGame(GetLevelId()).GetEntitiesInSquareArea
)


def GetEntitiesBySelector(selector, from_entity=""):
    # type: (str, str) -> list[str]
    return CF.CreateEntityComponent(from_entity).GetEntitiesBySelector(selector)


def GetEntityTypeFamily(entity_id):
    # type: (str) -> list[str]
    return CF.CreateAttr(entity_id).GetTypeFamily()


def GetDroppedItem(entity_id, get_user_data=False):
    # type: (str, bool) -> Item | None
    itemdict = CF.CreateItem(GetLevelId()).GetDroppedItem(entity_id, get_user_data)
    if itemdict is None:
        return None
    return Item.from_dict(itemdict)


def SpawnDroppedItem(dim, pos, item):
    # type: (int, tuple[float, float, float], Item) -> str | None
    return GetServer().CreateEngineItemEntity(item.marshal(), dim, pos)


def DestroyEntity(entity_id):
    # type: (str) -> bool
    return GetServer().DestroyEntity(entity_id)


def GetPos(entity_id):
    # type: (str) -> tuple[float, float, float]
    return CF.CreatePos(entity_id).GetPos()


def SetMotion(entity_id, motion):
    # type: (str, tuple[float, float, float]) -> bool
    return CF.CreateActorMotion(entity_id).SetMotion(motion)


def Hurt(
    entity_id,
    damage,
    cause,
    attackerId=None,
    childAttackerId=None,
    knocked=True,
    customTag=None,
):
    # type: (str, float, str, str | None, str | None, bool, str | None) -> bool
    return CF.CreateHurt(entity_id).Hurt(
        damage, cause, attackerId, childAttackerId, knocked, customTag
    )


__all__ = [
    "GetEntitiesInSquareArea",
    "GetEntitiesBySelector",
    "GetDroppedItem",
    "GetEntityTypeFamily",
    "GetPos",
    "Hurt",
    "SpawnDroppedItem",
    "SetMotion",
    "DestroyEntity",
]
