# coding=utf-8
"""
金属锤（`metal_hammer`）—— **工具，不是机器**：不吃电、没有耗时。

界面照 minijei 的 `metal_hammer_recipes`：中间**不是进度条**，而是三张
静态图叠出来的「正在锤」—— `arrow_img` + 转 -30° 的锤子 + 转 -15° 的锭。
这台本来就没有 `tick_duration`，摆一根不会动的进度条才是错的；
基类 `InitProgress` 找不到 `/progress/mask` 会自动跳过，Python 侧不用声明。

按钮用**横排**（`buttons_panel_horizontal`）—— 行只有 40px 高，
四颗按钮竖着排放不下。

典型配方：**铜锭 → 铜板**。
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:metal_hammer"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，
    不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "MetalHammerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiMetalHammer.RECIPES_GRID"
""" 配方页控件定义名。对应 resource_pack/ui/mei_recipes/MetalHammer.json """

INPUT_CELLS = 1
""" 布局上有几个输入格。**取该机器配方里最大的槽位数**，
    单条配方用不满是正常的（那几格渲染成空面板，语义就是"这条配方不用那一格"）"""


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.metal_hammer",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=103,
    )
