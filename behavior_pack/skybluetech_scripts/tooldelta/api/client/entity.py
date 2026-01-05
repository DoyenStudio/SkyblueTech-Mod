# coding=utf-8
from ...define.item import Item
from ...internal import ClientComp, ClientLevelId, GetClient
from ..internal.cacher import MethodCacher

_addDropItemToWorld = MethodCacher(lambda :ClientComp.CreateItem(ClientLevelId).AddDropItemToWorld)

def CreateDropItemModelEntity(dim, xyz, item, bob_speed=0, spin_speed=0):
    # type: (int, tuple[float, float, float], Item, float, float) -> str
    return _addDropItemToWorld(item.marshal(), dim, xyz, bob_speed, spin_speed)

def EvalMolangExpression(entity_id, expression):
    # type: (str, str) -> dict
    return ClientComp.CreateQueryVariable(entity_id).EvalMolangExpression(expression)

SetDropItemTransform = MethodCacher(lambda :ClientComp.CreateItem(ClientLevelId).SetDropItemTransform)
DeleteClientDropItemEntity = MethodCacher(lambda :ClientComp.CreateItem(ClientLevelId).DeleteClientDropItemEntity)
CreateClientEntity = MethodCacher(lambda :GetClient().CreateClientEntityByTypeStr)
DestroyClientEntity = MethodCacher(lambda :GetClient().DestroyClientEntity)
