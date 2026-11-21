# coding=utf-8
from ... import exports
from .._common import BuildMachine


def Build():
    icon_id, recipes = exports.Collection("OilFuelGeneratorRecipe")
    return BuildMachine(
        category_id=icon_id, icon_id=icon_id,
        name_key="tile.skybluetech:oilfuel_generator.name",
        recipes=recipes, sort_index=121,
    )
