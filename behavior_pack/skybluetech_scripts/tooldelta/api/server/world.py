# coding=utf-8
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_getRecipesByInput = MethodCacher(
    lambda: CF.CreateRecipe(GetLevelId()).GetRecipesByInput
)
_getRecipesByResult = MethodCacher(
    lambda: CF.CreateRecipe(GetLevelId()).GetRecipesByResult
)


def GetRecipesByInput(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByInput(item_id, recipe_tag, aux_value, maxResultNum)


def GetRecipesByResult(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByResult(item_id, recipe_tag, aux_value, maxResultNum)


GetLocalTime = MethodCacher(lambda: CF.CreateDimension(GetLevelId()).GetLocalTime)
IsRaining = MethodCacher(lambda: CF.CreateWeather(GetLevelId()).IsRaining)
GetRecipeByRecipeId = MethodCacher(
    lambda: CF.CreateRecipe(GetLevelId()).GetRecipeByRecipeId
)
GetSeed = MethodCacher(lambda: CF.CreateGame(GetLevelId()).GetSeed)
RegisterEntityAOIEvent = MethodCacher(
    lambda: CF.CreateDimension(GetLevelId()).RegisterEntityAOIEvent
)
UnRegisterEntityAOIEvent = MethodCacher(
    lambda: CF.CreateDimension(GetLevelId()).UnRegisterEntityAOIEvent
)


__all__ = [
    "GetRecipesByInput",
    "GetRecipesByResult",
    "GetRecipeByRecipeId",
    "GetLocalTime",
    "GetSeed",
    "IsRaining",
    "RegisterEntityAOIEvent",
    "UnRegisterEntityAOIEvent",
]
