# coding=utf-8
"""
工业研究（`industrial_researching`）—— **唯一一台不是机器的"机器"**。

它没有自己的方块：研究是在**机件加工台**上做的
（`client/ui/machinery/machinery_workstation.py:113` 推 `IndustrialResearchProgressUI`），
所以类型图标与工作站都取加工台 —— 玩家点着图标去找，得能找到真东西。

配方集合也不按机器 id 命名，蔚蓝里就叫 `"IndustrialResearching"`（`COLLECTION`），
研究配方类也没有自己的 `recipe_icon_id`，所以图标取加工台配方类的。

三处与别台不同（细节见 `ui_script.py`）：
  · 材料 **3~7 格不等**，布局照 minijei 排 **3×3**；
  · 产物两个（成果 + 刻印模版）且**槽位号随材料数浮动** ⇒ 按位置取；
  · 经验等级不是槽位，画成可见的 `xp_cost_label`。

> 数据侧实测最多只到 **7 格**，但布局按 minijei 排满 3×3：
> 格数跟**机器**走而不跟**当前数据**走，
> 蔚蓝以后加一条 8/9 材料的配方时这里不用改。

典型配方：**192 红石 + 72 石英 + 40 青金石 + 32 铜线圈 + 24 高级控制电路
+ 12 铜导线 + 4 蔚蓝核心 → 基础速度升级组件 + 刻印模版**，需要 **40 级经验**。
这条是 7 格满的那一条，正好验满格；再看一条 3 格的（如通用分流升级组件）
验剩下四格是空面板而不是错位。
"""
from .._common import BuildMachine
from ... import exports
from .ui_script import BuildUIScript, INPUT_CELLS

CATEGORY_ID = "skybluetech:industrial_researching"
CONTROL_DEF = "SkyblueMeiIndustrialResearching.RECIPES_GRID"
SORT_INDEX = 130

COLLECTION = "IndustrialResearching"
""" 研究配方集合的名字（`misc/industrial_researching.py` 建集合时给的），经正式导出的 get_collection 取 """


def Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """ 把经验等级搬进 Data。它在配方对象的属性上（也在 `extra_inputs` 里，
        但那份是 `[[槽位, id, 数量]]` 的通用形状，读起来绕） """
    level = getattr(sb_recipe, "require_exp_level", None)
    if level is not None:
        parts["data"]["require_exp_level"] = int(level)


def Build():  # type: () -> tuple
    recipes = exports.NamedCollection(COLLECTION)

    return BuildMachine(
        category_id=CATEGORY_ID,
        # 没有自己的方块 ⇒ 借加工台。玩家点图标要能找到真的去处
        icon_id=exports.IconOf(exports.WORKSTATION_RECIPE),
        name_key="skybluetech.mei.category.industrial_researching",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        decorate=Decorate,
        ui_script=BuildUIScript(CATEGORY_ID),
    )
