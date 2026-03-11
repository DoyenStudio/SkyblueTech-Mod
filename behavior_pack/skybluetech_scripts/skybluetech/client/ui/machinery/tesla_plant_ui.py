# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.api.client import CreateShapeFactory
from skybluetech_scripts.tooldelta.api.common import Delay
from ....common.events.machinery.tesla_plant import (
    TeslaPlantSettingsUpload,
    TeslaPlantSettingsUpdate,
)
from ....common.ui_sync.machinery.hover_text_displayer import HoverTextDisplayerUISync
from .define import MachinePanelUI, MAIN_PATH
from .utils import UpdatePowerBar

EDIT_BOX_NODE = MAIN_PATH / "edit_box"
TIP_LABEL_NODE = MAIN_PATH / "tip_label"
POWER_BAR_NODE = MAIN_PATH / "power_bar"
SETTING_PANEL_NODE = MAIN_PATH / "settings"
SWITCH_DO_ENABLE_NODE = SETTING_PANEL_NODE / "switch1"
SWITCH_DO_ATTACK_PLAYER_NODE = SETTING_PANEL_NODE / "switch2"
SWITCH_DO_ATTACK_MONSTER_NODE = SETTING_PANEL_NODE / "switch3"
RANGE_PREVIEW_BTN_NODE = SETTING_PANEL_NODE / "range_preview_btn"
RANGE_DISPLAY_LABEL_NODE = SETTING_PANEL_NODE / "range_display"
RANGE_ADD_BTN_NODE = SETTING_PANEL_NODE / "range_add_btn"
RANGE_SUB_BTN_NODE = SETTING_PANEL_NODE / "range_sub_btn"


@RegistToolDeltaScreen("TeslaPlantUI.main", is_proxy=True)
class TeslaPlantUI(MachinePanelUI):
    def OnCreate(self):
        self.sync = HoverTextDisplayerUISync.NewClient(self.dim, self.x, self.y, self.z)  # type: HoverTextDisplayerUISync
        self.sync.SetWhenUpdatedCallback(self.WhenUpdated)
        self.tip_label = self.GetElement(TIP_LABEL_NODE).asLabel()
        self.edit_box = self.GetElement(EDIT_BOX_NODE).asTextEditBox()
        self.power_bar = self.GetElement(POWER_BAR_NODE)
        self.range_display_label = self.GetElement(RANGE_DISPLAY_LABEL_NODE).asLabel()
        self.rane_preview_btn = (
            self
            .GetElement(RANGE_PREVIEW_BTN_NODE)
            .asButton()
            .SetCallback(self.on_preview_range)
        )
        self.range_add_btn = (
            self
            .GetElement(RANGE_ADD_BTN_NODE)
            .asButton()
            .SetCallback(self.on_add_range)
        )
        self.range_sub_btn = (
            self
            .GetElement(RANGE_SUB_BTN_NODE)
            .asButton()
            .SetCallback(self.on_sub_range)
        )
        self.switch_do_enable = self.GetElement(SWITCH_DO_ENABLE_NODE).asSwitch()
        self.switch_do_attack_player = self.GetElement(
            SWITCH_DO_ATTACK_PLAYER_NODE
        ).asSwitch()
        self.switch_do_attack_monster = self.GetElement(
            SWITCH_DO_ATTACK_MONSTER_NODE
        ).asSwitch()
        self.do_enable = False
        self.do_attack_player = False
        self.do_attack_monster = False
        self.working_range = 0

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)

    def upload_settings(self):
        TeslaPlantSettingsUpload(
            self.dim,
            self.x,
            self.y,
            self.z,
            self.working_range,
            self.do_enable,
            self.do_attack_monster,
            self.do_attack_player,
        ).send()

    def on_add_range(self, _):
        self.working_range += 1
        self.range_display_label.SetText(str(self.working_range))
        self.upload_settings()

    def on_sub_range(self, _):
        self.working_range -= 1
        self.range_display_label.SetText(str(self.working_range))
        self.upload_settings()

    def on_preview_range(self, _):
        start_preview(self.x, self.y, self.z, self.working_range)
        self.RemoveUI()

    @MachinePanelUI.Listen(TeslaPlantSettingsUpdate)
    def onContentUpdate(self, event):
        # type: (TeslaPlantSettingsUpdate) -> None
        self.do_enable = event.do_enable
        self.do_attack_player = event.do_attack_player
        self.do_attack_monster = event.do_attack_monster
        self.working_range = event.working_range
        self.range_display_label.SetText(str(event.working_range))
        self.switch_do_enable.SetState(event.do_enable)
        self.switch_do_attack_player.SetState(event.do_attack_player)
        self.switch_do_attack_monster.SetState(event.do_attack_monster)

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_1")
    def onSwitch1Toggled(self, params):
        self.do_enable = params["state"]
        self.upload_settings()

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_2")
    def onSwitch2Toggled(self, params):
        self.do_attack_player = params["state"]
        self.upload_settings()

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_3")
    def onSwitch3Toggled(self, params):
        self.do_attack_monster = params["state"]
        self.upload_settings()


previewing_shape = None


def start_preview(x, y, z, range):
    # type: (float, float, float, int) -> None
    global previewing_shape
    if previewing_shape is not None:
        return
    previewing_shape = CreateShapeFactory().AddBoxShape(
        (x - range, y - range, z - range), (range * 2, range * 2, range * 2)
    )
    finish_preview()


@Delay(8)
def finish_preview():
    global previewing_shape
    if previewing_shape is None:
        return
    previewing_shape.Remove()
    previewing_shape = None
