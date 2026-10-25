# coding=utf-8
"""
榨油机 —— **M3 的第一台流体机器**。

形状是骨架①「物 ⇄ 流体」里最简单的一支：物品进 → 流体出，一进一出。
所以它整台的代码就是下面这个参数表：布局与脚本都走通用那份
（`_common.BuildMachine`），差别只有 `output_kind="fluid"` 一个字符串。

典型配方：**向日葵种子 → 50 mB 植物油**（40 RF，60 游戏刻）。
另一条是小麦种子 → 5 mB，同一台机器上体积差 10 倍，正好用来看液面比例。

> 选它开路是因为它把「流体渲染」这条链单独摘了出来：贴图 → 染色 → 液面高度
> → hover 体积。**没有任何别的新东西**（无双输入、无多产出、无温度、无 RF），
> 一旦有问题，问题一定在这条链上。见 `skybluetech.md` §7.8.7-3。
"""
from .. import _common
from ... import convert, exports

CATEGORY_ID = "skybluetech:oil_extractor"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一 """

RECIPE_CLS = "OilExtractorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiOilExtractor.RECIPES_GRID"
""" 配方页控件定义名。对应 resource_pack/ui/mei_recipes/OilExtractor.json """

INPUT_CELLS = 1


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return _common.BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.oil_extractor",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=110,
        # 产物是流体 ⇒ 走 FluidPanel。布局那边同步把产物格换成 output_fluid
        output_kind=convert.CATEGORY_FLUID,
    )
