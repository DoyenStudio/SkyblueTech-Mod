# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.client.machinery.tesla_plant.range_preview import start_preview
from skybluetech_scripts.skybluetech.common.events.machinery.tesla_plant import (
    TeslaPlantSettingsUpload,
    TeslaPlantSettingsUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.tesla_plant import (
    DEFAULT_WORK_RANGE,
    K_SETTING_ATTACK_MOB,
    K_SETTING_ATTACK_MONSTER,
    K_SETTING_ATTACK_PLAYER,
    K_SETTING_WORK_RANGE,
    MAX_WORK_RANGE,
    MIN_WORK_RANGE,
    STORE_RF_MAX,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_BAR_PATH = MAIN_PATH / "power_bar"
SETTING_PANEL_PATH = MAIN_PATH / "settings"
SWITCH_DO_ATTACK_MOB_PATH = SETTING_PANEL_PATH / "switch1"
SWITCH_DO_ATTACK_PLAYER_PATH = SETTING_PANEL_PATH / "switch2"
SWITCH_DO_ATTACK_MONSTER_PATH = SETTING_PANEL_PATH / "switch3"
RANGE_PREVIEW_BTN_PATH = SETTING_PANEL_PATH / "range_preview_btn"
RANGE_DISPLAY_LABEL_PATH = SETTING_PANEL_PATH / "range_display"
RANGE_ADD_BTN_PATH = SETTING_PANEL_PATH / "range_add_btn"
RANGE_SUB_BTN_PATH = SETTING_PANEL_PATH / "range_sub_btn"


@RegistToolDeltaScreen("TeslaPlantUI.main", is_proxy=True)
class TeslaPlantUI(MachinePanelUIProxy):
    def OnCreate(self):
        self._settings_ready = False
        self._preview_pending = False
        self.dim, self.x, self.y, self.z = self.pos
        self.power_bar = self.GetElement(POWER_BAR_PATH)
        self.range_display_label = self.GetElement(RANGE_DISPLAY_LABEL_PATH).asLabel()
        self.GetElement(RANGE_PREVIEW_BTN_PATH).asButton().SetCallback(self.on_preview_range)
        self.GetElement(RANGE_ADD_BTN_PATH).asButton().SetCallback(self.on_add_range)
        self.GetElement(RANGE_SUB_BTN_PATH).asButton().SetCallback(self.on_sub_range)
        self.switch_do_attack_mob = self.GetElement(SWITCH_DO_ATTACK_MOB_PATH).asSwitch()
        self.switch_do_attack_player = self.GetElement(SWITCH_DO_ATTACK_PLAYER_PATH).asSwitch()
        self.switch_do_attack_monster = self.GetElement(SWITCH_DO_ATTACK_MONSTER_PATH).asSwitch()
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData((self.x, self.y, self.z))
        data = data["exData"] if data is not None else {}
        work_range = GetValue(data, K_SETTING_WORK_RANGE, DEFAULT_WORK_RANGE)
        if type(work_range) is not int or not MIN_WORK_RANGE <= work_range <= MAX_WORK_RANGE:
            work_range = DEFAULT_WORK_RANGE
        self.apply_settings(
            work_range,
            bool(GetValue(data, K_SETTING_ATTACK_MONSTER, True)),
            bool(GetValue(data, K_SETTING_ATTACK_MOB, False)),
            bool(GetValue(data, K_SETTING_ATTACK_PLAYER, False)),
        )
        self._settings_ready = True
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)

    def OnTicking(self):
        if not getattr(self, "_settings_ready", False):
            return
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData((self.x, self.y, self.z))
        if data is None:
            return
        UpdatePowerBar(self.power_bar, GetValue(data["exData"], K_STORE_RF, 0), STORE_RF_MAX)

    def apply_settings(self, work_range, do_attack_monster, do_attack_mob, do_attack_player):
        # Set fields first so programmatic toggle changes cannot echo uploads.
        self.work_range = work_range
        self.do_attack_monster = do_attack_monster
        self.do_attack_mob = do_attack_mob
        self.do_attack_player = do_attack_player
        self.range_display_label.SetText(str(work_range))
        self.switch_do_attack_mob.SetState(do_attack_mob)
        self.switch_do_attack_player.SetState(do_attack_player)
        self.switch_do_attack_monster.SetState(do_attack_monster)

    def upload_settings(self):
        if not self._settings_ready:
            return
        TeslaPlantSettingsUpload(
            self.dim,
            self.x,
            self.y,
            self.z,
            self.work_range,
            self.do_attack_monster,
            self.do_attack_mob,
            self.do_attack_player,
        ).send()

    def on_add_range(self, _):
        if self.work_range >= MAX_WORK_RANGE:
            return
        self.work_range += 1
        self.range_display_label.SetText(str(self.work_range))
        self.upload_settings()

    def on_sub_range(self, _):
        if self.work_range <= MIN_WORK_RANGE:
            return
        self.work_range -= 1
        self.range_display_label.SetText(str(self.work_range))
        self.upload_settings()

    def on_preview_range(self, _):
        if self._preview_pending:
            return
        self._preview_pending = True
        # Pop the native container outside its touch callback.
        ExecLater(0, self.close_and_preview)

    def close_and_preview(self):
        self.RemoveUI()
        start_preview(self.dim, self.x, self.y, self.z, self.work_range)

    @MachinePanelUIProxy.Listen(TeslaPlantSettingsUpdate)
    def on_content_update(self, event):
        # type: (TeslaPlantSettingsUpdate) -> None
        if not getattr(self, "_settings_ready", False):
            return
        if (event.dim, event.x, event.y, event.z) != self.pos:
            return
        self.apply_settings(
            event.work_range,
            event.do_attack_monster,
            event.do_attack_mob,
            event.do_attack_player,
        )

    def update_toggle(self, field, state):
        if not getattr(self, "_settings_ready", False):
            return
        state = bool(state)
        if getattr(self, field) == state:
            return
        setattr(self, field, state)
        self.upload_settings()

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_1")
    def on_mob_toggled(self, params):
        self.update_toggle("do_attack_mob", params["state"])

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_2")
    def on_player_toggled(self, params):
        self.update_toggle("do_attack_player", params["state"])

    @Binder.binding(Binder.BF_ToggleChanged, "#TeslaPlantUI.switch_3")
    def on_monster_toggled(self, params):
        self.update_toggle("do_attack_monster", params["state"])
