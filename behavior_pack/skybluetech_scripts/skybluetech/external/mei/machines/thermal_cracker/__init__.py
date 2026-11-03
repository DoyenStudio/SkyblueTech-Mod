# coding=utf-8
from .._common import BuildMachine
from ... import exports


def Decorate(recipe, parts):
    parts["data"]["conditions"] = [
        "流体数量为每批用量；200 tick 等效处理一份",
        "%g K < T ≤ %g K；%g K 满速" % (recipe.min_temperature, recipe.max_temperature, recipe.fit_temperature),
        "每批耗热 %g RF热；外部供热；任一输出堵塞均暂停" % recipe.heat_cost,
    ]


def Build():
    icon_id, recipes = exports.Collection("ThermalCrackerRecipe")
    return BuildMachine(category_id="skybluetech:thermal_cracker", icon_id=icon_id,
                        name_key="skybluetech.mei.category.thermal_cracker",
                        recipes=recipes, sort_index=119, decorate=Decorate)
