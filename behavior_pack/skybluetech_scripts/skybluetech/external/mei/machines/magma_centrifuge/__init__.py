# coding=utf-8
"""
高热流体离心机（`magma_centrifuge`）—— 一路流体分成最多四路。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/MagmaCentrifuge.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 产物槽位从 1 起编号（`fluid:1~6`，`fluid:0` 是输入）；**格数跟机器走**（六个产出口，当前数据最多用 4 路），
> 5、6 号照画成空格。液面按同方向最大体积归一（`CacheMaxVolume`），看得出谁多谁少。
典型配方：**100 mB 深板岩熔岩 → 18 轻质 + 60 中质 + 18 重质熔岩 + 4 熔融土**（80 RF/t × 100 刻）
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:magma_centrifuge"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "MagmaCentrifugeRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 116


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.magma_centrifuge",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
