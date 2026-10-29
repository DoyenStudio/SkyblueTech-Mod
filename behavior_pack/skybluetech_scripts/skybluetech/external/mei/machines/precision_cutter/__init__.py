# coding=utf-8
"""
精密切割机（`precision_cutter`）—— 物 + 切割刀（工具，不消耗）→ 物。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/PrecisionCutter.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 切割刀是工具：画成催化剂格（`cat/0`），候选是等级够的全部切割刀（等级表 `CUTTER_LEVEL_MAPPING` 顺着配方集合找到，
> 同机件加工台的工具）；等级与耐久消耗写进它的悬停。冷却液储罐是机器自己的（配方类只有物品），不画。
> 产物在 2 号槽 = 三个产出格最上面那格（内凹管道的箭头指着中间那格，机器界面本身就这样）。
典型配方：**海晶石 → 4 海晶碎片**（切割刀 1 级以上，每次耗 1 点耐久）
"""
from .._common import BuildMachine
from ... import exports
from ... import bridge, convert

CATEGORY_ID = "skybluetech:precision_cutter"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "PrecisionCutterRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 109


def _MakeDecorate(level_map):  # type: (dict) -> any
    """ 切割刀做催化剂：等级不低于配方要求的都认（同蔚蓝服务端 `recipe.cutter_level > level` 才拒） """
    def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
        data = parts["data"]
        level = int(getattr(sb_recipe, "cutter_level", 0) or 0)
        data["cutter_level"] = level
        cost = getattr(sb_recipe, "cutter_durability_cost", None)
        if cost is not None:
            data["cutter_durability_cost"] = int(cost)
        cutters = sorted(item_id for item_id, have in level_map.items() if int(have) >= level)
        stacks = convert.stacks_of(cutters)
        if stacks:
            parts["catalysts"].append(bridge.Types.Ingredient(stacks, 1))
    return _Decorate


def _Lore(recipe):  # type: (any) -> dict
    data = getattr(recipe, "Data", None) or {}
    lines = ["§7切割刀等级： §f%d 级以上" % int(data.get("cutter_level") or 0)]
    if data.get("cutter_durability_cost"):
        lines.append("§7每次消耗耐久： §f%d" % int(data["cutter_durability_cost"]))
    return {"mei_ui.recipe.cat0": "\n".join(lines)}


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.precision_cutter",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=_MakeDecorate(exports.OwnerConstant(recipes, "CUTTER_LEVEL_MAPPING", {}) or {}),
        lores=_Lore,
    )
