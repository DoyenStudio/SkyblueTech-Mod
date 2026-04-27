# coding=utf-8
import time
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ....common.mini_jei.core.define import CategoryType, RecipeBase


DISP_BOARD_KEY = "disp_board"
DISP_BOARD_SRC_KEY = "disp_board_src"


class ItemDisplayer(object):
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

    def onBtnReleased(self, _):
        fmt = GetItemHoverName(self.item.id) or self.item.id
        if self.prob != 1.0:
            fmt += "\n§e产出概率： %.1f%%%%" % (self.prob * 100)
        if self.tag is not None:
            fmt += "\n\n§8接受标签: " + self.tag
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        CreateDescBoard(
            self.ctrl,
            (x + sizex, y - sizey),
            CategoryType.ITEM,
            self.item.id,
            self.item.id,
            fmt,
        )


class RFOutputDisplayer(object):
    def __init__(self, ctrl, rf):
        # type: (UBaseCtrl, int) -> None
        from ..machinery.utils import FormatRF

        self.ctrl = ctrl
        self.rf = rf
        self.ctrl["rf_label"].asLabel().SetText(FormatRF(rf))


# def GetDoubleClickHelper(delay=0.25):
#     ticker = [0.0]

#     def onclick_cb():
#         nowtime = time.time()
#         if nowtime - ticker[0] < delay:
#             return True
#         ticker[0] = nowtime
#         return False

#     return onclick_cb


def CreateDescBoard(hang_ctrl, global_xy, category, item_id, display_item_id, text):
    # type: (UBaseCtrl, tuple[float, float], str, str, str, str) -> UBaseCtrl | None
    # RemoveDisplayBoard(ctrl._root)
    # screen_vars = ctrl._root._vars
    # databoard = ctrl._root.AddElement("SkybluePanelLib.DataTextScreen", "display_board")
    # databoard["image/label"].asLabel().SetText(text, sync_size=True)
    # databoard.SetLayer(100)

    from ....common.mini_jei import GetRecipesByInput, GetRecipesByOutput
    from .favourite_items import (
        IsFavourite,
        AddFavourite,
        RemoveFavourite,
    )
    from .recipe_checker_ui import RecipeCheckerUI

    ui_node = hang_ctrl._root
    if not isinstance(ui_node, RecipeCheckerUI):
        return None

    if "desc_board" in ui_node._vars:
        ui_node._vars.pop("desc_board").Remove()

    desc_board = ui_node.AddElement("RecipeCheckerUI.item_desc_panel", "desc_board")
    check_src_btn = desc_board["check_src_btn"].asButton()
    check_usage_btn = desc_board["check_usage_btn"].asButton()
    close_btn = desc_board["close_btn"].asButton()
    fav_btn = desc_board["fav_btn"].asButton()
    text_label = desc_board["text_panel/image/label"].asLabel()
    fav_img = fav_btn["favor"]

    item_src_recipes = {}  # type: dict[tuple[str, str], list[RecipeBase]]
    item_usage_recipes = {}  # type: dict[tuple[str, str], list[RecipeBase]]
    for recipe in GetRecipesByOutput(category, item_id):
        recipe_renderer = recipe.GetRendererForced()(recipe)
        item_src_recipes.setdefault(
            (
                recipe_renderer.recipe_icon_id,
                recipe_renderer.minijei_title
                or GetItemHoverName(recipe_renderer.recipe_icon_id),
            ),
            [],
        ).append(recipe)
    for recipe in GetRecipesByInput(category, item_id):
        recipe_renderer = recipe.GetRendererForced()(recipe)
        item_usage_recipes.setdefault(
            (
                recipe_renderer.recipe_icon_id,
                recipe_renderer.minijei_title
                or GetItemHoverName(recipe_renderer.recipe_icon_id),
            ),
            [],
        ).append(recipe)

    def on_check_src(_):
        ui_node.PushRecipes(item_src_recipes)
        ui_node._vars.pop("desc_board").Remove()

    def on_check_usage(_):
        ui_node.PushRecipes(item_usage_recipes)
        ui_node._vars.pop("desc_board").Remove()

    def on_close(_):
        ui_node._vars.pop("desc_board").Remove()

    def on_switch_favor(_):
        is_favourite = IsFavourite(category, item_id, display_item_id)
        if is_favourite:
            res = RemoveFavourite(category, item_id, display_item_id)
            if not res:
                print("[Warning] Failed to remove favourite item.")
        else:
            res = AddFavourite(category, item_id, display_item_id)
            if not res:
                print("[Warning] Failed to add favourite item.")
        fav_img.SetVisible(IsFavourite(category, item_id, display_item_id))
        ui_node._vars.pop("desc_board").Remove()

    check_src_btn.SetCallback(on_check_src)
    check_usage_btn.SetCallback(on_check_usage)
    close_btn.SetCallback(on_close)
    fav_btn.SetCallback(on_switch_favor)
    check_src_btn["disable_mask"].SetVisible(not item_src_recipes)
    check_usage_btn["disable_mask"].SetVisible(not item_usage_recipes)
    text_label.SetText(text)
    desc_board.SetPos(global_xy)
    desc_board.SetLayer(50)
    fav_img.SetVisible(IsFavourite(category, item_id, display_item_id))
    ui_node._vars["desc_board"] = desc_board

    return desc_board
