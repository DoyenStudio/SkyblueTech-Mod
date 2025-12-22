# coding=utf-8

from ...internal import ClientComp, ClientLevelId
from ..internal.cacher import MethodCacher


_getRecipesByInput = MethodCacher(lambda:ClientComp.CreateRecipe(ClientLevelId).GetRecipesByInput)
_getRecipesByResult = MethodCacher(lambda:ClientComp.CreateRecipe(ClientLevelId).GetRecipesByResult)

def GetRecipesByInput(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByInput(item_id, recipe_tag, aux_value, maxResultNum)

def GetRecipesByResult(item_id, recipe_tag, aux_value=0, maxResultNum=-1):
    # type: (str, str, int, int) -> list[dict]
    return _getRecipesByResult(item_id, recipe_tag, aux_value, maxResultNum)


__all__ = [
    "GetRecipesByInput",
    "GetRecipesByResult",
]
