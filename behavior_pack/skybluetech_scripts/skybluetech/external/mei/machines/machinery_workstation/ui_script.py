# coding=utf-8
"""
机件加工台的配方页脚本。

**与模板成型机不共用**：两者界面看着一样，但
  · 加工台**不吃电**（`MachineryWorkstationRecipe` 是 `Recipe` 直接子类，
    连 `power_cost` 字段都没有；机器 GUI 里也没有 power_bar）；
  · 模板机**吃电**（60 RF/t），布局要让出 20px 给电力条、行宽 208。

共用一份脚本就得在里面开「有没有电」的分支，而那个分支会随两台机器各自演化
越长越多。各自一份反而更短。共用的只剩下真正共用的东西：
基类的进度条/电力驱动（`_common.BuildBase`）与槽位簇（`inputs_9` / `side_slots`）。
"""
from ... import bridge
from .._common import BuildBase, IngredientForCell

_SCRIPT = None

SIDE_PREFIXES = ("mei_ui.recipe.side0", "mei_ui.recipe.side1")
""" 侧栏两格的绑定前缀。与模板机用同一对名字不要紧 ——
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

    class WorkstationUIScript(BuildBase()):
        """ 3×3 + 工具两格 + 产物。布局见 ui/mei_recipes/Workstation.json """

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

    _SCRIPT = WorkstationUIScript
    return _SCRIPT
