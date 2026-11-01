# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.skybluetech.common.mini_jei.core.define import CategoryType
from .render_utils import ItemDisplayer, CreateDescBoard


if 0>1:
    from skybluetech_scripts.skybluetech.common.mini_jei.core import Input


def UpdateRecipePower(ctrl, level, segments, hover):
    # type: (UBaseCtrl, float, int, str) -> None
    """共享配方布局的非平铺能量条；显示配方耗能，不显示机器储能。"""
    from skybluetech_scripts.tooldelta.define import UICtrlPosData
    from ..machinery.utils import _QuantizeEnergy, SetHoverText

    cache = ctrl._vars
    if "recipe_power_mask" not in cache:
        cache["recipe_power_mask"] = ctrl["bar/mask"]
    shown = _QuantizeEnergy(max(0.0, min(1.0, level)), segments)
    if cache.get("recipe_power_shown") != shown:
        cache["recipe_power_shown"] = shown
        cache["recipe_power_mask"].SetFullSize(
            "y", UICtrlPosData("parent", relative_value=shown)
        )
    SetHoverText(ctrl, hover)


def _format_recipe_fluid_volume(volume):
    # type: (float) -> str
    if volume == float("inf"):
        return "无限"
    if volume >= 10000:
        value, unit = volume / 1000.0, "B"
    else:
        value, unit = volume, "mB"
    text = str(value)
    if text.endswith(".0"):
        text = text[:-2]
    return text + " " + unit


class FluidDisplayer(object):
    """
    配方行里的流体格 (SkybluePanelLib.fluid_tank):
    液面按同一行同方向里最大的用量画; 悬停写配方用量 (不写储罐容量); 点击 (悬停层 info 是按钮) 弹出说明, 同物品格。
    """

    def __init__(self, ctrl, fluid_id, fluid_volume, max_volume, prob=1.0, not_consumed=False):
        # type: (UBaseCtrl, str, float, float, float, bool) -> None
        self.ctrl = ctrl
        self.fluid_id = fluid_id
        self.volume = fluid_volume
        self.max_volume = max_volume
        self.prob = prob
        self.not_consumed = not_consumed
        self.check_btn = ctrl["info"].asButton()
        self.check_btn.SetCallback(self.onBtnReleased)
        self.update()

    def update(self):
        from ..machinery.utils import FluidDisplayer, SetHoverText

        FluidDisplayer(self.ctrl, enable_interact=False).update(
            self.fluid_id, self.volume, self.max_volume or 1.0
        )
        SetHoverText(
            self.ctrl,
            "§d流体类型： §f"
            + (CF.CreateItem(LEVEL_ID).GetItemHoverName(self.fluid_id) or self.fluid_id)
            + self._get_detail_text(),
        )

    def _get_detail_text(self):
        text = "\n§a体积： §f" + _format_recipe_fluid_volume(self.volume)
        if self.not_consumed:
            text += "\n§e不被消耗。"
        if self.prob != 1.0:
            text += "\n§e产出概率： %.1f%%%%" % (self.prob * 100)
        return text

    def onBtnReleased(self, params):
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        CreateDescBoard(
            self.ctrl,
            (x + sizex / 2, y - sizey / 2),
            CategoryType.FLUID,
            self.fluid_id,
            self.fluid_id,
            "§d流体类型： §f"
            + (CF.CreateItem(LEVEL_ID).GetItemFormattedHoverText(self.fluid_id) or self.fluid_id)
            + self._get_detail_text(),
        )


class InputDisplayer(object):
    def __init__(self, ctrl, input):
        # type: (UBaseCtrl, Input) -> None
        self.ctrl = ctrl
        self.count = input.count
        self.aux = 0 if input.is_tag or input.aux == -1 else input.aux
        self.not_consumed = input.count == 0
        if input.is_tag:
            self.enable_carousel = True
            self.tag = input.id
            self.carousel_items = list(GetItemsByTag(self.tag))
            if not self.carousel_items:
                raise ValueError("tag2item not found: " + self.tag)
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

    def update(self):
        self.item_renderer.SetUiItem(
            Item(self.get_current_carousel_item(), self.aux, count=int(self.count))
        )
        self.item_count_label.SetText(
            str(int(self.count)) if self.count not in (0, 1) else ""
        )

    def tick(self, ui_ticks):
        # type: (int) -> None
        if ui_ticks % 30 == 0:
            self.carousel_index = (self.carousel_index + 1) % self.carousel_indices
            self.update()

    def get_current_carousel_item(self):
        return self.carousel_items[self.carousel_index]

    def onBtnReleased(self, params):
        current_disp_item_id = self.get_current_carousel_item()
        fmt = CF.CreateItem(LEVEL_ID).GetItemFormattedHoverText(current_disp_item_id) or current_disp_item_id
        if self.not_consumed:
            fmt += "\n§e不被消耗。"
        if self.tag is not None:
            fmt += "\n\n§8接受标签: " + self.tag
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        CreateDescBoard(
            self.ctrl,
            (x + sizex, y - sizey),
            CategoryType.ITEM,
            current_disp_item_id,
            current_disp_item_id,
            fmt,
        )


class MultiItemsDisplayer(object):
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

    def update(self):
        self.item_renderer.SetUiItem(self.get_current_carousel_item())

    def tick(self, ui_ticks):
        # type: (int) -> None
        if ui_ticks % 30 == 0 and len(self.carousel_items) > 1:
            self.carousel_index = (self.carousel_index + 1) % self.carousel_indices
            self.update()

    def get_current_carousel_item(self):
        return self.carousel_items[self.carousel_index]

    def onBtnReleased(self, params):
        current_disp_item = self.get_current_carousel_item()
        fmt = CF.CreateItem(LEVEL_ID).GetItemFormattedHoverText(current_disp_item.id) or current_disp_item.id
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        CreateDescBoard(
            self.ctrl,
            (x + sizex, y - sizey),
            CategoryType.ITEM,
            current_disp_item.id,
            current_disp_item.id,
            fmt,
        )
