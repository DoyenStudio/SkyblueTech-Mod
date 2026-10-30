# coding=utf-8
"""
机件加工台。

**它不是「N 进 1 出」**，所以既不用通用布局也不用通用脚本：
除了 3×3 的输入格与产物，它还要 **工具**（扳手 + 钳），摆在右上的侧栏两格。
界面与模板机看着同形，但**两者已解耦**：本机**不吃电**（next 框架起是 `MachineRecipe` 子类，
但功率与耗时恒为 0），而模板机吃电、行宽多 20px。各自一份布局（`Workstation.json`）与脚本（`ui_script.py`）。
等级要求不占界面位置，挂在工具格的 hover 文本上（`ItemPanel.SetLore`）。
工具是**催化剂** —— 不消耗，但决定这条配方做不做得成。

把工具做成 `Recipe.Catalysts` 换来一件事：**点一把扳手查用途，
能查到所有要用它的加工台配方**（MEI 的 `StaticRecipeSource` 会把催化剂
一并索引进「按材料查」的桶）。
"""
from ... import bridge, exports
from .._common import BuildMachine
from .ui_script import BuildUIScript

CATEGORY_ID = "skybluetech:machinery_workstation"
RECIPE_CLS = "MachineryWorkstationRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiWorkstation.RECIPES_GRID"
SORT_INDEX = 104

INPUT_CELLS = 9
""" 3×3。加工台的输入槽位号就是 0~8 """

ELECTRIC_WORKSTATION = "skybluetech:electric_machinery_workstation"
""" 电动机件加工台（N7）。方块 id 是公开的 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.machinery_workstation",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        decorate=_Decorate,
        ui_script=BuildUIScript(CATEGORY_ID, INPUT_CELLS, _SideSlot),
        # N7 电动机件加工台做的是同一张表（只多挂一个工作站，页面不改）
        stations=(icon_id, ELECTRIC_WORKSTATION),
    )


# 工具 —— 等级门槛与催化剂
# ======================================================================================================================
def _LevelName(level):  # type: (any) -> str
    """ 等级的显示名（"铁" / "殷钢"），取导出配方类自带的 LEVEL_MAPPING；对不上返回空串 """
    cls = getattr(exports.Recipes(), exports.WORKSTATION_RECIPE, None)
    name = (getattr(cls, "LEVEL_MAPPING", None) or {}).get(level, "")
    # 要随 hover 文本递给引擎, 而引擎收到 unicode 不抛不报、只是安静地取不到东西
    return name.encode("utf-8") if isinstance(name, unicode) else name  # noqa


def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """ 补上工具催化剂与等级。由 `MachineRecipeSource` 在转换每条配方时调 """
    wrench_level = int(getattr(sb_recipe, "wrench_level", 1) or 1)
    pincer_level = int(getattr(sb_recipe, "pincer_level", 1) or 1)

    Ingredient = bridge.Types.Ingredient
    catalysts = []
    # 判据是「**至少**这个等级」，铁级配方连殷钢扳手也认 ——
    # 拿着殷钢扳手查用途的玩家应该看到全部配方，而不是只有殷钢那些
    for kind, level in (("wrench", wrench_level), ("pincer", pincer_level)):
        stacks = bridge.Registry.ItemFactory.GetStacksFromIds(
            exports.WorkstationTools(kind, level))
        # 拿不到就放个空的占位: 槽位与 Data 里的等级必须对得上,
        # 删掉会让"第 0 个催化剂是扳手"这条约定失效
        catalysts.append(Ingredient(stacks) if stacks else Ingredient([]))

    parts["catalysts"] = catalysts
    parts["data"].update({
        "wrench_level": wrench_level,
        "pincer_level": pincer_level,
        "craft_times": int(getattr(sb_recipe, "craft_times", 1) or 1),
    })


def _SideSlot(recipe, index):  # type: (any, int) -> tuple
    """
    侧栏第 index 格：0 = 扳手，1 = 钳。返回 (Ingredient, lore)

    工具是**催化剂**，所以从 `GetCatalysts()` 取而不是 `GetInputs()`。
    `_Decorate` 里即便物品取不到也会放一个空 Ingredient 占位，
    就是为了这条下标约定不会错位。
    """
    catalysts = recipe.GetCatalysts()
    slot = catalysts[index] if index < len(catalysts) else None
    key = ("wrench_level", "pincer_level")[index] if index < 2 else None
    label = ("扳手", "钳")[index] if index < 2 else ""
    lore = None
    if key:
        data = getattr(recipe, "Data", None) or {}
        level = _LevelName(data.get(key))
        if level:
            lore = "§7需要 {}等级: §f{}".format(label, level)
    return slot, lore
