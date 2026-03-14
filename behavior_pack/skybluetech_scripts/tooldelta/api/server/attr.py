# coding=utf-8
from mod.server.extraServerApi import GetEngineCompFactory

CF = GetEngineCompFactory()


def GetEntityAttr(entity_id, attr_enum):
    # type: (str, int) -> float
    return CF.CreateAttr(entity_id).GetAttrValue(attr_enum)


def GetEntityAttrMaxValue(entity_id, attr_enum):
    # type: (str, int) -> float
    return CF.CreateAttr(entity_id).GetAttrMaxValue(attr_enum)


def SetEntityAttr(entity_id, attr_enum, value):
    # type: (str, int, float) -> bool
    return CF.CreateAttr(entity_id).SetAttrValue(attr_enum, value)


__all__ = [
    "GetEntityAttr",
    "GetEntityAttrMaxValue",
    "SetEntityAttr",
]
