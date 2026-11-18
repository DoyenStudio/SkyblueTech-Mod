# coding=utf-8
from .._common import BuildMachine
from ... import exports


def Build():
    icon_id, recipes = exports.Collection("FlotationMachineRecipe")
    return BuildMachine(category_id=icon_id, icon_id=icon_id,
                        name_key="skybluetech.mei.category.flotation_machine",
                        recipes=recipes, sort_index=121)
