# coding=utf-8
from .._common import BuildMachine
from ... import exports


def Build():
    icon_id, recipes = exports.Collection("SmallChemicalReactorRecipe")
    return BuildMachine(category_id="skybluetech:small_chemical_reactor", icon_id=icon_id,
                        name_key="skybluetech.mei.category.small_chemical_reactor",
                        recipes=recipes, sort_index=120)
