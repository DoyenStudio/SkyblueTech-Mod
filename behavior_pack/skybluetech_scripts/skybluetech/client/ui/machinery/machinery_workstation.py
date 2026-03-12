# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ....common.events.machinery.machinery_workstation import (
    MachineryWorkstationDoCraft,
)
from ....common.ui_sync.machinery.machinery_workstation import (
    MachineryWorkstationUISync,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdateGenericProgressL2R

from ..recipe_checker import AsRecipeCheckerBtn
from ....common.machinery_def.machinery_workstation import recipes

WARNING_BAR_DISPLAY_THRESOLD = 0.8

CRAFT_BTN_NODE = MAIN_PATH / "craft_btn"
CRAFT_SPEED_BAR_NODE = MAIN_PATH / "craft_speed_bar"
WARNING_BAR_NODE = MAIN_PATH / "warning_bar"
PRGS_NODE = MAIN_PATH / "progress"
OUTPUT_ITEM_PREVIEWER_NODE = (
    MAIN_PATH / "output_slot/slot/item_cell_overlay_ref/item_renderer"
)

craft_hi_freq_limiter = PlayerRateLimiter(0.1)


@RegistToolDeltaScreen("MachineryWorkstationUI.main", is_proxy=True)
class MachineryWorkstationUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = MachineryWorkstationUISync.NewClient(dim, x, y, z)  # type: MachineryWorkstationUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.craft_strength = 0.0
        self.warning_bar_shown = False
        self.warning_bar_display_time = 0
        self.craft_btn = (
            self.GetElement(CRAFT_BTN_NODE).asButton().SetCallback(self.onClickCraftBtn)
        )
        self.craft_speed_bar = self.GetElement(CRAFT_SPEED_BAR_NODE).asImage()
        self.warning_bar = self.GetElement(WARNING_BAR_NODE)
        self.output_item_previewer = self.GetElement(
            OUTPUT_ITEM_PREVIEWER_NODE
        ).asItemRenderer()
        self.progress_bar = self.GetElement(PRGS_NODE)
        self.warning_bar.SetVisible(False)
        self.output_item_previewer.SetVisible(False)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,  # pyright: ignore[reportArgumentType]
        )

    def OnTicking(self):
        self.craft_strength = max(0.0, self.craft_strength - 0.01)
        self.warning_bar_display_time = max(0, self.warning_bar_display_time - 1)
        self.update_craft_speed_bar()

    def onClickCraftBtn(self, _):
        _, x, y, z = self.pos
        if not craft_hi_freq_limiter.record():
            return
        if self.sync.output_item_id is None:
            return
        self.craft_strength = min(1.0, self.craft_strength + 0.3)
        MachineryWorkstationDoCraft(x, y, z, self.craft_strength).send()

    def WhenUpdated(self):
        if self.sync.output_item_id is None:
            self.output_item_previewer.SetVisible(False)
        else:
            self.output_item_previewer.SetVisible(True)
            self.output_item_previewer.SetUiItem(Item(self.sync.output_item_id))
            UpdateGenericProgressL2R(self.progress_bar, self.sync.progress)

    def update_craft_speed_bar(self):
        self.craft_speed_bar.SetSpriteClipRatio(
            "fromRightToLeft",
            1 - self.craft_strength,
        )
        if self.craft_strength >= WARNING_BAR_DISPLAY_THRESOLD:
            self.warning_bar_display_time = 60
        if self.warning_bar_display_time > 0:
            if not self.warning_bar_shown:
                self.warning_bar.SetVisible(True)
                self.warning_bar_shown = True
        else:
            if self.warning_bar_shown:
                self.warning_bar.SetVisible(False)
                self.warning_bar_shown = False
