# coding=utf-8
import time
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import (
    UBaseCtrl,
    UScreenNode,
    UScreenProxy,
    ToolDeltaScreen,
)
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ...mini_jei import CategoryType


DISP_BOARD_KEY = "disp_board"
DISP_BOARD_SRC_KEY = "disp_board_src"


class ItemDisplayer:
    def __init__(self, ctrl, item, tag=None, prob=1.0):
        # type: (UBaseCtrl, Item, str | None, float) -> None
        self.ctrl = ctrl
        self.item = item
        self.tag = tag
        self.prob = prob
        self.item_renderer = ctrl["item_renderer"].asItemRenderer()
        self.item_count_label = ctrl["item_count"].asLabel()
        self.prob_label = ctrl["prob"].asLabel()
        self.check_btn = ctrl["check_btn"].asButton()
        self.check_btn.SetCallback(self.onBtnReleased)
        self.update()
        self.item_renderer.SetVisible(True)
        self.double_click_detecter = GetDoubleClickDetecter()

    def UpdateItem(self, item):
        # type: (Item) -> None
        self.item = item
        self.update()

    def update(self):
        if self.item.count not in (0, 1):
            self.item_count_label.SetText(str(self.item.count))
        else:
            self.item_count_label.SetText("")
        self.item_renderer.SetUiItem(self.item)
        if self.prob != 1.0:
            self.prob_label.SetText("%.1f%%%%" % (self.prob * 100))

    def onBtnReleased(self, params):
        if self.double_click_detecter():
            from ...ui.recipe_checker.recipe_checker_ui import RecipeCheckerUI

            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.renderRecipesOfInput(self.item.id, CategoryType.ITEM)
            return
        if NeedRemoveDisplayBoard(self.ctrl):
            RemoveDisplayBoard(self.ctrl._root)
            return
        fmt = GetItemHoverName(self.item.id) or self.item.id
        if self.prob != 1.0:
            fmt += "\n§e产出概率： %.1f%%%%" % (self.prob * 100)
        if self.tag is not None:
            fmt += "\n\n§8接受标签: " + self.tag
        databoard = CreateDisplayBoard(self.ctrl, fmt)
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y - (sizey / 2 + csizey / 2)))


def GetDoubleClickDetecter(delay=0.25):
    ticker = [0.0]

    def onclick_cb():
        nowtime = time.time()
        if nowtime - ticker[0] < delay:
            return True
        ticker[0] = nowtime
        return False

    return onclick_cb


def RemoveDisplayBoard(root):
    # type: (UScreenNode | UScreenProxy | ToolDeltaScreen) -> None
    screen_vars = root._vars
    if DISP_BOARD_KEY in screen_vars:
        screen_vars.pop(DISP_BOARD_KEY).Remove()
    if screen_vars.get(DISP_BOARD_SRC_KEY):
        screen_vars.pop(DISP_BOARD_SRC_KEY)


def NeedRemoveDisplayBoard(ctrl):
    # type: (UBaseCtrl) -> bool
    screen_vars = ctrl._root._vars
    return DISP_BOARD_KEY in screen_vars and screen_vars.get(DISP_BOARD_SRC_KEY) is ctrl


def CreateDisplayBoard(ctrl, text):
    # type: (UBaseCtrl, str) -> UBaseCtrl
    RemoveDisplayBoard(ctrl._root)
    screen_vars = ctrl._root._vars
    databoard = ctrl._root.AddElement("SkybluePanelLib.DataTextScreen", "display_board")
    databoard["image/label"].asLabel().SetText(text, sync_size=True)
    databoard.SetLayer(100)
    screen_vars[DISP_BOARD_KEY] = databoard
    screen_vars[DISP_BOARD_SRC_KEY] = ctrl
    return databoard
