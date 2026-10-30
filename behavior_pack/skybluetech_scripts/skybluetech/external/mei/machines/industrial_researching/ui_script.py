# coding=utf-8
"""
工业研究的配方页脚本。

两处与通用脚本不同，都是这台机器独有的：

  1. **产物槽位随配方浮动**。`IndustrialResearchingRecipe.__init__` 把产物放在
     `item:len(require_items)` 与 `+1`（`mini_jei/misc/industrial_researching.py:20`），
     而 `require_items` 是 3~7 个不等 ⇒ 产物槽号在 `item:3` 到 `item:8` 之间跑。
     **所以只能按位置取 `GetOutputs()[i]`，不能按槽位反查** ——
     反查要先知道槽号，而槽号本身是变量。
     按位置是安全的：`convert._split` 已按 `(种类, 槽位号)` 排过序，
     两个产物的相对顺序（成果在前、刻印模版在后）是定的。

  2. **经验等级要显示**。`exp_lv` 不是槽位（没有身份、不进物品表、
     点了查不出用途），落在 `Data["extra_inputs"]` 里，
     由 `Labels` 推成可见的 `xp_cost_label` —— 照 minijei，不藏 hover。
"""
from ... import bridge
from .._common import BuildBase, IngredientForCell

_SCRIPT = None


INPUT_CELLS = 9
""" 布局上的材料格数。**照 minijei 排 3×3**
    （它的渲染器取 `require_items[:9]`，用不满的 `SetVisible(False)`）。
    实测数据最多只到 7 格，但格数跟机器走而不跟当前数据走 ——
    蔚蓝以后加一条 8/9 材料的配方时，这里不用改 """


def Labels(recipe):  # type: (any) -> dict
    """
    经验消耗。**可见文字不是 hover** —— 照 minijei
    （`panel["xp_cost_label"].SetText("花费经验 Lv %s")`）：
    这是读这条配方必须看到的数，藏进 hover 等于让玩家先猜再验证。
    """
    data = getattr(recipe, "Data", None) or {}
    level = int(data.get("require_exp_level") or 0)
    if level <= 0:
        return {}
    return {"/xp_cost_label": "花费经验 Lv %d" % level}


def BuildUIScript(category_id):  # type: (str) -> type
    """ 造工业研究的配方页脚本；重复调用返回同一份 """
    global _SCRIPT
    if _SCRIPT is not None:
        return _SCRIPT

    RecipeBinder = bridge.UI.Binding.RecipeBinder
    render_slot = bridge.UI.Slots.render_slot

    input_prefixes = ["mei_ui.recipe.input%d" % i for i in range(INPUT_CELLS)]
    output_prefixes = ["mei_ui.recipe.output0", "mei_ui.recipe.output1"]

    class ResearchingUIScript(BuildBase()):
        """ 3×3 材料 + 经验 → 刻印模版 + 成果。
            布局见 ui/mei_recipes/IndustrialResearching.json """

        TYPE = category_id
        LABELS = staticmethod(Labels)

        def __init__(self, recipe):
            BuildBase().__init__(self, recipe)
            self.InputControls = {}
            self.OutputControls = {}

        def InitControls(self):
            for i in range(INPUT_CELLS):
                self.InputControls[i] = self.Child("/input/{}".format(i))
            for i in range(len(output_prefixes)):
                self.OutputControls[i] = self.Child("/output/{}".format(i))

        @RecipeBinder.Group(input_prefixes)
        def InputPanelCallback(self, index):
            control = self.InputControls.get(index)
            if control is None:
                return None
            # 材料槽位是**连续的** `item:0..N-1`，格子下标恰好就是槽位号 ⇒
            # 这一半可以按槽位反查（与浮动的产物侧不同）
            entry = IngredientForCell(self.Recipe, index)
            panel = render_slot(control, entry)
            # **用不满的格子整个藏起来**，与 minijei 一致
            # （`IndustrialResearchingRecipeRenderer` 对 `index >= len(require_items)`
            # 的格子调 `SetVisible(False)`）。布局排满 3×3 是跟机器走的，
            # 而一条只要 3 样材料的配方不该显示 6 个空槽 —— 那看着像"还能再放"。
            # 底下那块 `slots_bg` 灰板照常露出来，正是 minijei 的样子。
            panel.SetChildVisible(entry is not None)
            return panel

        @RecipeBinder.Group(output_prefixes)
        def OutputPanelCallback(self, index):
            control = self.OutputControls.get(index)
            if control is None:
                return None
            outputs = self.Recipe.GetOutputs()
            return render_slot(
                control, outputs[index] if index < len(outputs) else None)

    _SCRIPT = ResearchingUIScript
    return _SCRIPT
