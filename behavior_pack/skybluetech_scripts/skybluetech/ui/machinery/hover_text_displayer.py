# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from ...define.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from ...ui_sync.machinery.hover_text_displayer import HoverTextDisplayerUISync
from .define import MachinePanelUI, MAIN_PATH
from .utils import UpdatePowerBar

EDIT_BOX_NODE = MAIN_PATH / "edit_box"
TIP_LABEL_NODE = MAIN_PATH / "tip_label"
POWER_BAR_NODE = MAIN_PATH / "power_bar"


@RegistToolDeltaScreen("ItemSplitterUI.main")
class HoverTextDisplayerUI(MachinePanelUI):
    EXIT_BTN_PATH = "close_btn"

    def OnCreate(self):
        self.sync = HoverTextDisplayerUISync.NewClient(self.dim, self.x, self.y, self.z)  # type: HoverTextDisplayerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.tip_label = self.GetElement(TIP_LABEL_NODE).asLabel()
        self.edit_box = self.GetElement(EDIT_BOX_NODE).asTextEditBox()
        self.power_bar = self.GetElement(POWER_BAR_NODE)
        self.onContentUpdate(
            HoverTextDisplayerContentUpdate.unmarshal(
                self._init_params["st:init_content"]
            )
        )

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)

    @MachinePanelUI.Listen(HoverTextDisplayerContentUpdate)
    def onContentUpdate(self, event):
        # type: (HoverTextDisplayerContentUpdate) -> None
        self.edit_box.SetText(event.new_text)
        self.tip_label.SetText("投影内容    耗能: %d RF/t" % event.power_cost)

    @Binder.binding(Binder.BF_EditFinished, "#HoverTextDisplayerUI.text_edit_box")
    def oneEditedText(self, params):
        text = params["Text"]  # type: str
        HoverTextDisplayerContentUpload(self.x, self.y, self.z, text[:512]).send()
