# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.ui_keys import (
    HOVER_TEXT_DISPLAYER_UI,
)
from skybluetech_scripts.skybluetech.common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.hover_text_displayer import (
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode

from .define import SCREEN_BASE_PATH, MachinePanelUI
from .utils import UpdatePowerBar

EDIT_BOX_PATH = SCREEN_BASE_PATH / "edit_box"
TIP_LABEL_PATH = SCREEN_BASE_PATH / "tip_label"
POWER_BAR_PATH = SCREEN_BASE_PATH / "power_bar"


@RegistToolDeltaScreen("HoverTextDisplayerUI.main", key=HOVER_TEXT_DISPLAYER_UI)
class HoverTextDisplayerUI(MachinePanelUI):
    EXIT_BTN_PATH = SCREEN_BASE_PATH / "close_btn"
    allow_esc_exit = True

    def OnCreate(self):
        self.tip_label = self.GetElement(TIP_LABEL_PATH).asLabel()
        self.edit_box = self.GetElement(EDIT_BOX_PATH).asTextEditBox()
        self.power_bar = self.GetElement(POWER_BAR_PATH)
        self.onContentUpdate(
            HoverTextDisplayerContentUpdate.unmarshal(
                self._init_params["st:init_content"]
            )
        )

    def OnTicking(self):
        if not self.inited:
            return
        data = GetBlockEntityData(self.x, self.y, self.z)
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)

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
