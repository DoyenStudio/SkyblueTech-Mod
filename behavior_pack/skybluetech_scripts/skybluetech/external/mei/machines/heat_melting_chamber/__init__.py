# coding=utf-8
from .._common import BuildMachine
from ... import exports


def Decorate(recipe, parts):
    parts["data"]["conditions"] = [
        "最低 / 最适 / 最高温度： %g / %g / %g K"
        % (recipe.min_temperature, recipe.fit_temperature, recipe.max_temperature),
        "§7[§e!§7] §7过热会导致流体§e直接蒸发散失",
    ]


def Build():
    icon_id, recipes = exports.Collection("HeatMeltingChamberRecipe")
    return BuildMachine(
        category_id="skybluetech:heat_melting_chamber",
        icon_id=icon_id,
        name_key="skybluetech.mei.category.heat_melting_chamber",
        recipes=recipes,
        sort_index=118,
        decorate=Decorate,
    )
