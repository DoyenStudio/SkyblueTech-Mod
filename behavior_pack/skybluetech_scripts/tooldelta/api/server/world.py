# coding=utf-8

from ...internal import ServerComp, ServerLevelId
from ..internal.cacher import MethodCacher


_getRecipesByInput = MethodCacher(lambda:ServerComp.CreateRecipe(ServerLevelId).GetRecipesByInput)
_getRecipesByResult = MethodCacher(lambda:ServerComp.CreateRecipe(ServerLevelId).GetRecipesByResult)


def GetRecipesByInput(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByInput(item_id, recipe_tag, aux_value, maxResultNum)

def GetRecipesByResult(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByResult(item_id, recipe_tag, aux_value, maxResultNum)

GetLocalTime = ServerComp.CreateDimension(ServerLevelId).GetLocalTime
IsRaining = ServerComp.CreateWeather(ServerLevelId).IsRaining
GetRecipeByRecipeId = MethodCacher(lambda:ServerComp.CreateRecipe(ServerLevelId).GetRecipeByRecipeId)


__all__ = [
    "GetRecipesByInput",
    "GetRecipesByResult",
    "GetRecipeByRecipeId",
    "GetLocalTime",
    "IsRaining",
]
