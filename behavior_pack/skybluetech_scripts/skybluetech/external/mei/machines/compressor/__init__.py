# coding=utf-8
"""
压缩机。

一台「N 进 1 出」的机器要的东西全在 `_machine.BuildMachine` 里，
本模块只声明它的身份参数。加一台机器就照抄本文件。
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:compressor"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，
    不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "CompressorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiCompressor.RECIPES_GRID"
""" 配方页控件定义名。对应 resource_pack/ui/mei_recipes/Compressor.json """

INPUT_CELLS = 3
""" 布局上有几个输入格。**取该机器配方里最大的槽位数**，
    单条配方用不满是正常的（那几格渲染成空面板，语义就是"这条配方不用那一格"）"""


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.compressor",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=101,
    )
