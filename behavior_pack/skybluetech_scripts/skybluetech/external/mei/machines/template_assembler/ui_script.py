# coding=utf-8
"""
模板成型机的配方页脚本。

**与机件加工台不再共用**（2026-09-05 解耦）：两者界面看着一样，但
  · 本机**吃电**（60 RF/t），布局要让出 20px 给电力条、行宽 208；
  · 加工台**不吃电**（连 `power_cost` 字段都没有），行宽 188。

另一处实质差别：侧栏两格在本机是**真输入**（在 `input_slots` 里），
在加工台是**催化剂**（工具，不消耗）。
共用的只剩下真正共用的东西：基类的进度条/电力驱动（`_common.BuildBase`）
与槽位簇（`inputs_9` / `side_slots`）。
"""
from ... import bridge
from .._common import BuildBase, IngredientForCell

_SCRIPT = None

SIDE_PREFIXES = ("mei_ui.recipe.side0", "mei_ui.recipe.side1")
""" 侧栏两格的绑定前缀。与加工台用同一对名字不要紧 ——
    一个配方页里只有一种配方类型活着，前缀不会互相干扰 """


def BuildUIScript(category_id, grid_cells, side_getter):
    # type: (str, int, any) -> type
    """ 造加工台的配方页脚本；重复调用返回同一份 """
    global _SCRIPT
    if _SCRIPT is not None:
        return _SCRIPT

    RecipeBinder = bridge.UI.Binding.RecipeBinder
    render_slot = bridge.UI.Slots.render_slot
    grid_prefixes = ["mei_ui.recipe.input%d" % i for i in range(grid_cells)]

    class TemplateAssemblerUIScript(BuildBase()):
        """ 3×3 + 刻印模版/焊锡两格 + 产物 + 电力条。布局见 ui/mei_recipes/TemplateAssembler.json """

        TYPE = category_id
        GRID_CELLS = grid_cells

        def __init__(self, recipe):
            BuildBase().__init__(self, recipe)
            self.GridControls = {}
            self.SideControls = {}
            self.OutputControl = None

        def InitControls(self):
            for i in range(self.GRID_CELLS):
                self.GridControls[i] = self.Child("/input/{}".format(i))
            for i in range(len(SIDE_PREFIXES)):
                self.SideControls[i] = self.Child("/side/{}".format(i))
            self.OutputControl = self.Child("/output/0")

        @RecipeBinder.Group(grid_prefixes)
        def GridPanelCallback(self, index):
            control = self.GridControls.get(index)
            if control is None:
                return None
            return render_slot(control, IngredientForCell(self.Recipe, index))

        @RecipeBinder.Group(list(SIDE_PREFIXES))
        def SidePanelCallback(self, index):
            control = self.SideControls.get(index)
            if control is None:
                return None
            slot, lore = side_getter(self.Recipe, index)
            return render_slot(control, slot).SetLore(lore)

        @RecipeBinder.Group(["mei_ui.recipe.output"])
        def OutputPanelCallback(self, index):
            _ = index
            return render_slot(self.OutputControl, self.Recipe.GetPrimaryOutput())

    _SCRIPT = TemplateAssemblerUIScript
    return _SCRIPT
