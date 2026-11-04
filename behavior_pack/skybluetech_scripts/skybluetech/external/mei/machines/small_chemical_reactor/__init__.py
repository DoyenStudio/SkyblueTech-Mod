# coding=utf-8
from .._common import BuildMachine
from ... import exports


def _Decorate(recipe, parts):
    if "item:2" in parts["input_slots"]:
        index = parts["input_slots"].index("item:2")
        parts["input_slots"].pop(index)
        parts["catalysts"].append(parts["inputs"].pop(index))


def _Lore(recipe):
    return {"mei_ui.recipe.cat0": "§7催化剂（不消耗）"}


def Build():
    icon_id, recipes = exports.Collection("SmallChemicalReactorRecipe")
    return BuildMachine(category_id="skybluetech:small_chemical_reactor", icon_id=icon_id,
                        name_key="skybluetech.mei.category.small_chemical_reactor",
                        recipes=recipes, sort_index=120,
                        decorate=_Decorate, lores=_Lore)
