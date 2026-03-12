# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode
from ....common.define.ui_keys import HOVER_TEXT_DISPLAYER_UI
from ....common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from ....common.ui_sync.machinery.hover_text_displayer import HoverTextDisplayerUISync
from .define import MachinePanelUI, SCREEN_BASE_PATH
from .utils import UpdatePowerBar

EDIT_BOX_NODE = SCREEN_BASE_PATH / "edit_box"
TIP_LABEL_NODE = SCREEN_BASE_PATH / "tip_label"
POWER_BAR_NODE = SCREEN_BASE_PATH / "power_bar"


@RegistToolDeltaScreen("HoverTextDisplayerUI.main", key=HOVER_TEXT_DISPLAYER_UI)
class HoverTextDisplayerUI(MachinePanelUI):
    EXIT_BTN_PATH = SCREEN_BASE_PATH / "close_btn"
    allow_esc_exit = True

    def OnCreate(self):
        self.sync = HoverTextDisplayerUISync.NewClient(self.dim, self.x, self.y, self.z)  # type: HoverTextDisplayerUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
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
        HoverTextDisplayerContentUpload(
            self.x, self.y, self.z, py2_unicode(text)[:512]
        ).send()
