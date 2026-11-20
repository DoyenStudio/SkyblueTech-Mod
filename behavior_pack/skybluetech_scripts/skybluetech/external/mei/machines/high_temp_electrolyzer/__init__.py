# coding=utf-8
from skybluetech_scripts.skybluetech.external.mei import exports
from skybluetech_scripts.skybluetech.external.mei.machines._common import BuildMachine


def _decorate(recipe, parts):
    parts["data"]["conditions"] = recipe.conditions()


def Build():
    icon_id, recipes = exports.Collection("HighTempElectrolyzerRecipe")
    return BuildMachine(
        category_id=icon_id, icon_id=icon_id,
        name_key="skybluetech.mei.category.high_temp_electrolyzer",
        recipes=recipes, sort_index=128, decorate=_decorate,
    )
