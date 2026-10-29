# coding=utf-8
"""
发酵池（`fermenter`，多方块结构）—— 接种物 + 营养物 → 气体 + 流体，连续产出。

配方页照蔚蓝 UI 规范 v2：池体、滑条、温度文字不画（机器状态，不是配方的内容）；
两个产出槽往左挪到输入一列右边，主体在行里纵向居中。布局在 `_layouts.py`。

**数据不是配方集合**：`FermenterRecipe`（`common.machinery_def.fermenter.spec_recipes`），没有槽位、没有固定的量 ——
产量随菌群浓度与池内体积变化。所以：配方自己拼（`runtime.ListRecipeSource`），产物格不写体积（`volume_hidden`），
适宜温度写进进度（气泡计）的悬停。**导出缺口**：配方表不在 `common.export` 里，经 `exports.InternalModule` 取，见 `skybluetech.md` §8.11。

典型配方：**泥土（接种）+ 生物质碎屑（营养）→ 甲烷 + 沼气发酵泥**（25 ~ 40 °C，最适 30 °C）
"""
from .._common import BuildMachine
from ... import exports, runtime

CATEGORY_ID = "skybluetech:fermenter"
CONTROLLER = "skybluetech:fermenter_controller"
""" 控制器方块（配方页的图标与工作站）。方块 id 是公开的 """

SORT_INDEX = 131

POWER_NOTE = "3 RF/t 起（离适宜温度越远越多）"
""" 蔚蓝服务端：适宜区间里 3 RF/t，低于 25 °C 或高于 30 °C 每差 1 °C 多 1 RF/t """

INPUT_LORES = ("§7接种物（放进接种槽，菌群长起来就不再要）", "§7营养物（菌群一直在吃）")
OUTPUT_LORE = "§7连续产出：量随菌群浓度与池内体积变化"


def Build():  # type: () -> tuple
    module = exports.InternalModule("common.machinery_def.fermenter")
    table = dict(getattr(module, "spec_recipes", None) or {})
    if not table:
        raise LookupError("发酵池的配方表 spec_recipes 是空的")

    def make():  # type: () -> list
        recipes = []
        for _, sb_recipe in sorted(table.items()):
            data = {
                "power_note": POWER_NOTE,
                "volume_hidden": True,
                "conditions": ["§7适宜温度： §f%s ~ %s °C（最适 %s °C）" % (
                    _Number(sb_recipe.min_temperature), _Number(sb_recipe.max_temperature),
                    _Number(sb_recipe.fit_temperature))],
            }
            recipes.append(runtime.MakeRecipe(
                CATEGORY_ID,
                [("item", 0, sb_recipe.vitality_matter, 1, 1), ("item", 1, sb_recipe.nutrition_matter, 1, 1)],
                [("fluid", 0, sb_recipe.out_gas_id, 1, 1), ("fluid", 1, sb_recipe.out_fluid_id, 1, 1)],
                data))
        return recipes

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=CONTROLLER,
        name_key="skybluetech.mei.category.fermenter",
        sort_index=SORT_INDEX,
        source=runtime.Build().ListRecipeSource(CATEGORY_ID, make),
        lores=_Lore,
    )


def _Lore(recipe):  # type: (any) -> dict
    _ = recipe
    return {
        "mei_ui.recipe.input0": INPUT_LORES[0],
        "mei_ui.recipe.input1": INPUT_LORES[1],
        "mei_ui.recipe.output0": OUTPUT_LORE,
        "mei_ui.recipe.output1": OUTPUT_LORE,
    }


def _Number(value):  # type: (float) -> str
    value = float(value)
    return "%d" % int(value) if value == int(value) else "%.1f" % value
