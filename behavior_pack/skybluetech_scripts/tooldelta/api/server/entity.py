# coding=utf-8
#
from ...define.item import Item
from ...internal import ServerComp, ServerLevelId, GetServer


def GetEntitiesBySelector(selector, from_entity=""):
    # type: (str, str) -> list[str]
    return ServerComp.CreateEntityComponent(from_entity).GetEntitiesBySelector(selector)


def GetDroppedItem(entity_id, get_user_data=False):
    # type: (str, bool) -> Item
    return Item.from_dict(
        ServerComp.CreateItem(ServerLevelId).GetDroppedItem(entity_id, get_user_data)
    )


def SpawnDroppedItem(dim, pos, item):
    # type: (int, tuple[float, float, float], Item) -> None
    GetServer().CreateEngineItemEntity(item.marshal(), dim, pos)


def DestroyEntity(entity_id):
    # type: (str) -> None
    GetServer().DestroyEntity(entity_id)


def GetPos(entity_id):
    # type: (str) -> tuple[float, float, float]
    return ServerComp.CreatePos(entity_id).GetPos()


__all__ = [
    "GetEntitiesBySelector",
    "GetDroppedItem",
    "GetPos",
    "SpawnDroppedItem",
    "DestroyEntity",
]
