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

def SetQueryMolang(entity_id, var_name, value):
    # type: (str, str, float) -> bool
    return ClientComp.CreateQueryVariable(entity_id).Set(var_name, value)

RegisterQueryMolang = MethodCacher(lambda:ClientComp.CreateQueryVariable(ClientLevelId).Register)


__all__ = [
    "GetRecipesByInput",
    "GetRecipesByResult",
    "SetQueryMolang",
    "RegisterQueryMolang",
]
