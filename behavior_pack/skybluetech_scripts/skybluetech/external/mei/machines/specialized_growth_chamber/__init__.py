# coding=utf-8
from .._common import BuildMachine
from ... import exports


def _Decorate(recipe, parts):
    for slot in (1, 2):
        key = "item:%d" % slot
        if key in parts["input_slots"]:
            index = parts["input_slots"].index(key)
            parts["input_slots"].pop(index)
            parts["catalysts"].append(parts["inputs"].pop(index))
    parts["data"]["conditions"] = ["§7作物与培养基不消耗"]


def _Lore(recipe):
    return {
        "mei_ui.recipe.cat0": "§7作物（不消耗）",
        "mei_ui.recipe.cat1": "§7培养基（不消耗）",
    }


def Build():
    icon_id, recipes = exports.Collection("SpecializedGrowthChamberRecipe")
    return BuildMachine(category_id="skybluetech:specialized_growth_chamber", icon_id=icon_id,
                        name_key="skybluetech.mei.category.specialized_growth_chamber",
                        recipes=recipes, sort_index=121,
                        decorate=_Decorate, lores=_Lore)
