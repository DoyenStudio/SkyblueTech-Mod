# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from ...define.item import Item
from ...internal import GetClient
from ..common.cacher import MethodCacher


CF = GetEngineCompFactory()

_addDropItemToWorld = MethodCacher(
    lambda: CF.CreateItem(GetLevelId()).AddDropItemToWorld
)


def CreateDropItemModelEntity(dim, xyz, item, bob_speed=0, spin_speed=0):
    # type: (int, tuple[float, float, float], Item, float, float) -> str
    return _addDropItemToWorld(item.marshal(), dim, xyz, bob_speed, spin_speed)


def EvalMolangExpression(entity_id, expression):
    # type: (str, str) -> dict
    return CF.CreateQueryVariable(entity_id).EvalMolangExpression(expression)


def GetFootPos(entity_id):
    # type: (str) -> tuple[float, float, float]
    return CF.CreatePos(entity_id).GetFootPos()


def SetPosForClientEntity(entity_id, xyz):
    # type: (str, tuple[float, float, float]) -> bool
    return CF.CreatePos(entity_id).SetPosForClientEntity(xyz)


SetDropItemTransform = MethodCacher(
    lambda: CF.CreateItem(GetLevelId()).SetDropItemTransform
)
DeleteClientDropItemEntity = MethodCacher(
    lambda: CF.CreateItem(GetLevelId()).DeleteClientDropItemEntity
)
CreateClientEntity = MethodCacher(lambda: GetClient().CreateClientEntityByTypeStr)
DestroyClientEntity = MethodCacher(lambda: GetClient().DestroyClientEntity)
