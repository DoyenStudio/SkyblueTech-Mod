# coding=utf-8
#
from ...define.item import Item
from ...internal import ServerComp, ServerLevelId, GetServer
from ..internal.cacher import MethodCacher


GetEntitiesInSquareArea = MethodCacher(
    lambda: ServerComp.CreateGame(ServerLevelId).GetEntitiesInSquareArea
)


def GetEntitiesBySelector(selector, from_entity=""):
    # type: (str, str) -> list[str]
    return ServerComp.CreateEntityComponent(from_entity).GetEntitiesBySelector(selector)


def GetDroppedItem(entity_id, get_user_data=False):
    # type: (str, bool) -> Item | None
    itemdict = ServerComp.CreateItem(ServerLevelId).GetDroppedItem(
        entity_id, get_user_data
    )
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
    return ServerComp.CreatePos(entity_id).GetPos()


def SetMotion(entity_id, motion):
    # type: (str, tuple[float, float, float]) -> bool
    return ServerComp.CreateActorMotion(entity_id).SetMotion(motion)


__all__ = [
    "GetEntitiesInSquareArea",
    "GetEntitiesBySelector",
    "GetDroppedItem",
    "GetPos",
    "SpawnDroppedItem",
    "SetMotion",
    "DestroyEntity",
]
