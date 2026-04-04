# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from .define import CategoryType
from .render_utils import (
    ItemDisplayer,
    GetDoubleClickDetecter,
    CreateDisplayBoard,
    NeedRemoveDisplayBoard,
    RemoveDisplayBoard,
)

if 0:
    from . import Input


class FluidDisplayer:
    def __init__(self, ctrl, fluid_id, fluid_volume, max_volume):
        # type: (UBaseCtrl, str, float, float) -> None
        self.ctrl = ctrl
        self.fluid_id = fluid_id
        self.volume = fluid_volume
        self.max_volume = max_volume
        self.check_btn = ctrl["data_btn"].asButton()
        self.check_btn.SetCallback(self.onBtnReleased)
        self.update()
        self.double_click_detecter = GetDoubleClickDetecter()

    def update(self):
        from ....client.ui.machinery.utils import UpdateFluidDisplay

        UpdateFluidDisplay(self.ctrl, self.fluid_id, self.volume, self.max_volume)

    def onBtnReleased(self, params):
        from ....client.ui.machinery.utils import FormatFluidVolume

        if self.double_click_detecter():
            from ....client.ui.recipe_checker import RecipeCheckerUI

            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.render_recipes_of_input(self.fluid_id, CategoryType.FLUID)
            return
        if NeedRemoveDisplayBoard(self.ctrl):
            RemoveDisplayBoard(self.ctrl._root)
            return
        databoard = CreateDisplayBoard(
            self.ctrl,
            "§d流体类型： §f"
            + (GetItemHoverName(self.fluid_id) or self.fluid_id)
            + "\n"
            + "§a体积： §f"
            + FormatFluidVolume(self.volume),
        )
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y))


class InputDisplayer:
    def __init__(self, ctrl, input):
        # type: (UBaseCtrl, Input) -> None
        self.ctrl = ctrl
        if input.is_tag:
            self.enable_carousel = True
            self.tag = input.id
            self.carousel_items = list(GetItemsByTag(self.tag))
            self.carousel_indices = len(self.carousel_items)
        else:
            self.enable_carousel = False
            self.tag = None
            self.carousel_items = [input.id]
            self.carousel_indices = 1
        self.carousel_index = 0
        self.item_renderer = ctrl["item_renderer"].asItemRenderer()
        self.item_count_label = ctrl["item_count"].asLabel()
        self.prob_label = ctrl["prob"].asLabel()
        self.check_btn = ctrl["check_btn"].asButton()
        self.check_btn.SetCallback(self.onBtnReleased)
        self.update()
        self.item_renderer.SetVisible(True)
        self.double_click_detecter = GetDoubleClickDetecter()

    def update(self):
        self.item_renderer.SetUiItem(Item(self.get_current_carousel_item()))

    def tick(self, ui_ticks):
        # type: (int) -> None
        if ui_ticks % 30 == 0:
            self.carousel_index = (self.carousel_index + 1) % self.carousel_indices
            self.update()

    def get_current_carousel_item(self):
        return self.carousel_items[self.carousel_index]

    def onBtnReleased(self, params):
        current_disp_item_id = self.get_current_carousel_item()
        if self.double_click_detecter():
            from ....client.ui.recipe_checker.recipe_checker_ui import RecipeCheckerUI

            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.render_recipes_of_input(current_disp_item_id, CategoryType.ITEM)
            return
        if NeedRemoveDisplayBoard(self.ctrl):
            RemoveDisplayBoard(self.ctrl._root)
            return
        fmt = GetItemHoverName(current_disp_item_id) or current_disp_item_id
        if self.tag is not None:
            fmt += "\n\n§8接受标签: " + self.tag
        databoard = CreateDisplayBoard(self.ctrl, fmt)
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y - (sizey / 2 + csizey / 2)))


class MultiItemsDisplayer:
    def __init__(self, ctrl, items):
        # type: (UBaseCtrl, list[Item]) -> None
        self.ctrl = ctrl
        self.carousel_items = items
        self.carousel_index = 0
        self.carousel_indices = len(self.carousel_items)
        self.item_renderer = ctrl["item_renderer"].asItemRenderer()
        self.item_count_label = ctrl["item_count"].asLabel()
        self.prob_label = ctrl["prob"].asLabel()
        self.check_btn = ctrl["check_btn"].asButton()
        self.check_btn.SetCallback(self.onBtnReleased)
        self.update()
        self.item_renderer.SetVisible(True)
        self.double_click_detecter = GetDoubleClickDetecter()

    def update(self):
        self.item_renderer.SetUiItem(self.get_current_carousel_item())

    def tick(self, ui_ticks):
        # type: (int) -> None
        if ui_ticks % 30 == 0:
            self.carousel_index = (self.carousel_index + 1) % self.carousel_indices
            self.update()

    def get_current_carousel_item(self):
        return self.carousel_items[self.carousel_index]

    def onBtnReleased(self, params):
        current_disp_item = self.get_current_carousel_item()
        if self.double_click_detecter():
            from ....client.ui.recipe_checker.recipe_checker_ui import RecipeCheckerUI

            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.render_recipes_of_input(current_disp_item.id, CategoryType.ITEM)
            return
        if NeedRemoveDisplayBoard(self.ctrl):
            RemoveDisplayBoard(self.ctrl._root)
            return
        fmt = GetItemHoverName(current_disp_item.id) or current_disp_item.id
        databoard = CreateDisplayBoard(self.ctrl, fmt)
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y - (sizey / 2 + csizey / 2)))
