# coding=utf-8
from ... import exports
from .._common import BuildMachine


def Decorate(sb_recipe, parts):
    parts["allow_empty_outputs"] = True
    parts["data"]["rate_text"] = sb_recipe.RateText()
    parts["data"]["conditions"] = [sb_recipe.BiomeText()]


def Labels(recipe):
    return {"/rate": recipe.Data["rate_text"]}


def Build():
    icon_id, recipes = exports.Collection("EffluentOutfallRecipe")
    return BuildMachine(
        category_id=icon_id, icon_id=icon_id,
        name_key="tile.skybluetech:effluent_outfall.name", recipes=recipes,
        sort_index=122, decorate=Decorate, labels=Labels,
    )
