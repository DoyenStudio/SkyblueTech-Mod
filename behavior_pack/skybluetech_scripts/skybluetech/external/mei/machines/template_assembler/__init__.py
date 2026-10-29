# coding=utf-8
"""
模版成型机（`template_assembler`）—— 3×3 材料 + 焊锡锭 + 刻印模版（不消耗）→ 产物。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度（转动的齿轮）都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/TemplateAssembler.json` 同一次生成）。原来自己的配方页脚本（3×3 + 侧栏两格）随之删掉：
网格 0~8 与焊锡锭（第 10 格）是普通输入格，刻印模版是催化剂格（`cat/0`），都由 `_common._LayoutScriptFor` 画。

典型配方：**升级基板 + 2 通量核心 + 2 铜棒 + 金板 + 橡胶 + 基础电路 + 焊锡锭（刻印模版不消耗）→ 基础能效升级**
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:template_assembler"
RECIPE_CLS = "TemplateAssemblerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 107

TEMPLATE_LORE = "§7需要刻印对应的内容（不消耗）"


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.template_assembler",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=_Decorate,
        lores=_Lore,
    )


def _Lore(recipe):  # type: (any) -> dict
    _ = recipe
    return {"mei_ui.recipe.cat0": TEMPLATE_LORE}


def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """
    补上刻印模版 —— **做催化剂，不进原料**。

    模版只用来决定做哪条配方，蔚蓝做配方时不扣它；放进原料的话 MEI 会把它当成消耗品，
    收藏栏展开这条配方时还跟着倍数乘（实机发现）。
    当催化剂也照样查得到：点模版查用途，`StaticRecipeSource` 会把催化剂一并索引进「按材料查」。
    """
    from ... import bridge

    template_id = _TemplateId(sb_recipe)
    stacks = bridge.Registry.ItemFactory.GetStacksFromIds([template_id]) if template_id else []
    if not stacks:
        return
    held = set(getattr(stack.Item, "ItemId", None) for catalyst in parts["catalysts"] for stack in catalyst.get_stacks())
    if template_id not in held:
        parts["catalysts"].append(bridge.Types.Ingredient(stacks, 1))


def _TemplateId(sb_recipe):  # type: (any) -> str or None
    """ 刻印模版的物品 id：配方的 GetInputs() 比 inputs 多出来的那一项；取不到返回 None """
    # 模版 id 不在导出里，但蔚蓝的 GetInputs() 会把它补进第 9 格（给 MiniJEI 显示用），
    # 从配方对象自己身上取，就不用依赖 id_enum 的常量
    get_inputs = getattr(sb_recipe, "GetInputs", None)
    if get_inputs is None:
        return None
    declared = set(("tag:" + e.id) if getattr(e, "is_tag", False) else e.id
                   for e in (getattr(sb_recipe, "inputs", None) or {}).get("item", {}).values())
    for item_id in (get_inputs() or {}).get("item", []):
        if item_id not in declared and not item_id.startswith("tag:"):
            return item_id
    return None
