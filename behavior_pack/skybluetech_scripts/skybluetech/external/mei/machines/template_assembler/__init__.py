# coding=utf-8
"""
模版成型机。

槽位比别的机器多两格，而且有一格**不在数据里**：

  0~8   材料网格（现有配方只用到 0~5）
  9     刻印模版 —— `sb_recipe.inputs` 里**没有它**，它只出现在对方的
        `GetInputs()` 里（那是给 minijei 显示用的旁路）。不补就少一格。
  10    焊锡锭（在 `TemplateAssemblerRecipe.__init__` 里被塞进 inputs）
  11    产物

所以它要一个 `decorate` 去补第 9 格。
界面与加工台看着同形，但 **2026-09-05 已解耦**：本机**吃电**（60 RF/t），
布局要让出 20px 给电力条、行宽 208；加工台不吃电、行宽 188。
各自一份布局（`TemplateAssembler.json`）与脚本（`ui_script.py`）。
"""
from .._common import BuildMachine
from ... import exports
from .ui_script import BuildUIScript

CATEGORY_ID = "skybluetech:template_assembler"
RECIPE_CLS = "TemplateAssemblerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiTemplateAssembler.RECIPES_GRID"
SORT_INDEX = 107

GRID_CELLS = 9
""" 材料网格 0~8 """

SLOT_TEMPLATE = 9
""" 刻印模版所在的槽位 """

SLOT_SOLDERING = 10
""" 焊锡锭所在的槽位 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.template_assembler",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=_Decorate,
        ui_script=BuildUIScript(CATEGORY_ID, GRID_CELLS, _SideSlot),
    )


def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """
    补上第 9 格的刻印模版。

    **它必须按槽位号插到正确位置**：`input_slots` 与 `inputs` 是一一对应的两张表，
    界面靠槽位号反查（`_common.IngredientForCell`），插错位置就渲染到别的格子上。
    """
    from ... import bridge, convert

    slots = parts["input_slots"]
    key = convert.slot_key(convert.CATEGORY_ITEM, SLOT_TEMPLATE)
    if key in slots:
        return

    template_id = _TemplateId(sb_recipe)
    stacks = bridge.Registry.ItemFactory.GetStacksFromIds([template_id]) if template_id else []
    ingredient = bridge.Types.Ingredient(stacks, 1) if stacks \
        else bridge.Types.Ingredient([])

    # 找插入点, 保持与 convert._split 同序(先类别、后槽位号)。
    # **按编号比而不是按键字符串**: 字符串序下 "item:10" < "item:2" 会排错。
    # 本机只有物品输入, 非物品条目一律排在前面(类别名 "fluid" < "item"), 跳过即可
    position = len(slots)
    for index, existing in enumerate(slots):
        if not existing.startswith(convert.CATEGORY_ITEM + ":"):
            continue
        if convert.slot_number(existing) > SLOT_TEMPLATE:
            position = index
            break
    slots.insert(position, key)
    parts["inputs"].insert(position, ingredient)


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


def _SideSlot(recipe, index):  # type: (any, int) -> tuple
    """
    侧栏第 index 格：0 = 刻印模版，1 = 焊锡锭。返回 (Ingredient, lore)

    与加工台不同，这两样是**真输入**（在 input_slots 里），所以按真实槽位号反查
    —— 网格只用到 0~5 时，第 9 格在列表里的下标并不是 9。
    """
    from .._common import IngredientForCell

    slot_no = (SLOT_TEMPLATE, SLOT_SOLDERING)[index] if index < 2 else None
    if slot_no is None:
        return None, None
    lore = "§7需要刻印对应的内容" if slot_no == SLOT_TEMPLATE else None
    return IngredientForCell(recipe, slot_no), lore
