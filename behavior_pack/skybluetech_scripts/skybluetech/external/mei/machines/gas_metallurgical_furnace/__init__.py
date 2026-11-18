# coding=utf-8
from .._common import BuildMachine
from ... import exports


def _Decorate(recipe, parts):
    parts["data"]["total_rf"] = recipe.total_rf
    parts["data"]["conditions"] = [recipe.title, "整批耗电：%d RF" % recipe.total_rf]


def Build():
    icon_id, recipes = exports.Collection("GasMetallurgicalFurnaceRecipe")
    return BuildMachine(category_id=icon_id, icon_id=icon_id,
                        name_key="skybluetech.mei.category.gas_metallurgical_furnace",
                        recipes=recipes, sort_index=125, decorate=_Decorate)
