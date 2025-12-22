# coding=utf-8
import time
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl, UScreenNode, UScreenProxy
from skybluetech_scripts.tooldelta.plugins.allitems_getter import GetItemsByTag, allitems_by_tag
from skybluetech_scripts.tooldelta.plugins.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
)
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ...define.machine_config.define import MachineRecipe
from ...mini_jei import CategoryType, GenericFurnaceRecipe, GenericCraftingTableRecipe
from ...utils.fmt import FormatRF as _formatRF, FormatFluidVolume as _formatFluidVolume
from ..machines.utils import UpdateFluidDisplay


DISP_BOARD_KEY = "disp_board"
DISP_BOARD_SRC_KEY = "disp_board_src"



class ItemDisplayer:
    def __init__(self, ctrl, item, tag=None):
        # type: (UBaseCtrl, Item, str | None) -> None
        self.ctrl = ctrl
        self.item = item
        self.tag = tag
        self.item_renderer = ctrl["item_renderer"].asItemRenderer()
        self.item_count_label = ctrl["item_count"].asLabel()
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

    def onBtnReleased(self, params):
        if self.double_click_detecter():
            from .recipe_checker_ui import RecipeCheckerUI
            root = self.ctrl._root
            if isinstance(root, RecipeCheckerUI):
                root.renderRecipesOfInput(self.item.id, CategoryType.ITEM)
            return
        if NeedRemoveDisplayBoard(self.ctrl):
            return
        fmt = GetItemHoverName(self.item.id) or self.item.id
        if self.tag is not None:
            fmt += "\n\n§8接受标签: " + self.tag
        databoard = CreateDisplayBoard(self.ctrl, fmt)
        x, y = self.ctrl.GetRootPos()
        sizex, sizey = self.ctrl.GetSize()
        csizex, csizey = databoard.GetSize()
        databoard.SetPos((x + sizex / 2 + csizex / 2, y -(sizey / 2 + csizey / 2)))


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
        UpdateFluidDisplay(self.ctrl, self.fluid_id, self.volume, self.max_volume)

    def onBtnReleased(self, params):
        if self.double_click_detecter():
            from .recipe_checker_ui import RecipeCheckerUI
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
        

def RenderGenericMachineRecipe(panel, recipe):
    # type: (UBaseCtrl, MachineRecipe) -> None
    input_items = recipe.inputs.get("item", {})
    for slot, input in input_items.items():
        item = input.id
        is_tag = input.is_tag
        if is_tag:
            try:
                item_id = next(iter(GetItemsByTag(item)))
            except StopIteration:
                raise ValueError("tag2item not found: " + item)
        else:
            item_id = item
        ItemDisplayer(
            panel["slot%d" % slot],
            Item(item_id, count=int(input.count)),
            tag=item if is_tag else None,
        )
    output_items = recipe.outputs.get("item", {})
    for slot, input in output_items.items():
        item_id = input.id
        ItemDisplayer(panel["slot%d" % slot], Item(item_id, count=int(input.count)))
    input_fluids = recipe.inputs.get("fluid", {})
    if input_fluids:
        max_input_fluid_volume = max(input_fluids.values(), key=lambda x: x.count).count
    for slot, input in input_fluids.items():
        FluidDisplayer(
            panel["fluid%d" % slot],
            input.id, input.count, max_input_fluid_volume
        )
    output_fluids = recipe.outputs.get("fluid", {})
    if output_fluids:
        max_output_fluid_volume = max(output_fluids.values(), key=lambda x: x.count).count
    for slot, output in output_fluids.items():
        FluidDisplayer(
            panel["fluid%d" % slot],
            output.id, output.count, max_output_fluid_volume
        )


def RenderCraftingTableRecipe(panel, recipe):
    # type: (UBaseCtrl, GenericCraftingTableRecipe) -> None
    if isinstance(recipe.base, CraftingRecipeRes):
        pat_mapping = recipe.base.pattern_key
        for row, rowln in enumerate(recipe.base.pattern):
            for col, pat in enumerate(rowln):
                if pat == " ":
                    continue
                item = pat_mapping[pat]
                ItemDisplayer(
                    panel["slot%d" % (row * 3 + col)],
                    Item(item.item_id, item.aux_value)
                )
    else:
        for i, input in enumerate(recipe.base.inputs):
            ItemDisplayer(panel["slot%d" % i], Item(input.item_id, input.aux_value))
    ItemDisplayer(panel["slot9"], Item(
        recipe.base.result[0].item_id,
        recipe.base.result[0].aux_value,
        recipe.base.result[0].count,
    ))

def RenderFurnaceRecipe(panel, recipe):
    # type: (UBaseCtrl, GenericFurnaceRecipe) -> None
    ItemDisplayer(panel["slot0"], Item(recipe.base.input_item_id))
    ItemDisplayer(panel["slot1"], Item(recipe.base.output.item_id, recipe.base.output.aux_value))

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
    # type: (UScreenNode | UScreenProxy) -> None
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

