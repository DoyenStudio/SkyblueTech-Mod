# coding=utf-8
from .._common import BuildMachine
from ... import exports


def Decorate(recipe, parts):
    parts["data"]["conditions"] = recipe.heat_conditions()


def Build():
    icon_id, recipes = exports.Collection("IndustrialCentrifugeRecipe")
    return BuildMachine(category_id=icon_id, icon_id=icon_id,
                        name_key="skybluetech.mei.category.industrial_centrifuge",
                        recipes=recipes, sort_index=123, decorate=Decorate)
