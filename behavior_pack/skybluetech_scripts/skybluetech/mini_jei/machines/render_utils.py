# coding=utf-8
import time
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ...utils.fmt import FormatRF as _formatRF, FormatFluidVolume as _formatFluidVolume
from ..core import CategoryType
from ..core.render_utils import (
    GetDoubleClickDetecter,
    CreateDisplayBoard,
    NeedRemoveDisplayBoard,
    RemoveDisplayBoard,
)


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
        from ...ui.machinery.utils import UpdateFluidDisplay
        UpdateFluidDisplay(self.ctrl, self.fluid_id, self.volume, self.max_volume)

    def onBtnReleased(self, params):
        if self.double_click_detecter():
            from ...ui.recipe_checker import RecipeCheckerUI
            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.renderRecipesOfInput(self.fluid_id, CategoryType.FLUID)
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
            + _formatFluidVolume(self.volume)
        )
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y))





