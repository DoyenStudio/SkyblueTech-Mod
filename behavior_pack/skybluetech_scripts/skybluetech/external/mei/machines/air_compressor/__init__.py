# coding=utf-8
"""
空气压缩机（`air_compressor`）—— 零输入 → 流体（看所在维度）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/AirCompressor.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 零输入配方：只能按产物查（点压缩空气），查用途查不到它。维度写进箭头的悬停（名字表 `DIMENSION_NAMES` 顺着配方集合找到）。
典型配方：**（无输入）→ 50 mB 压缩空气**（主世界，40 RF/t × 10 刻）
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:air_compressor"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "AirCompressorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 126


def _MakeDecorate(names):  # type: (dict) -> any
    def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
        dimension = getattr(sb_recipe, "dimension", None)
        if dimension is not None:
            parts["data"]["conditions"] = ["§7维度： §f%s" % names.get(dimension, "未知")]
    return _Decorate


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.air_compressor",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=_MakeDecorate(exports.OwnerConstant(recipes, "DIMENSION_NAMES", {}) or {}),
    )
