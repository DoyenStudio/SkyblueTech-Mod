# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.ui_keys import ENERGY_CUBE_UI
from skybluetech_scripts.skybluetech.common.events.machinery.energy_cube import (
    EnergyCubeActionRequest,
    EnergyCubeSetIOModes,
    EnergyCubeStatesUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.energy_cube import (
    K_INPUT_POWER,
    K_IO_MODE,
    K_OUTPUT_POWER,
    STORE_RF_MAX,
    IOModes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import (
    GetValueWithDefault as GetValue,
)
from skybluetech_scripts.tooldelta.utils.nbt import (
    NBT2Py,
)

from .define import SCREEN_BASE_PATH, MachinePanelUI
from .utils import FormatRF, UpdateGenericProgressL2R

UPPER_PANEL_PATH = SCREEN_BASE_PATH / "upper"
LOWER_PANEL_PATH = SCREEN_BASE_PATH / "lower"
ENERGY_LABEL_PATH = UPPER_PANEL_PATH / "battery_icon/energy_label"
TOTAL_POWER_PATH = UPPER_PANEL_PATH / "total_power"
BATTERY_ICON_PATH = UPPER_PANEL_PATH / "battery_icon"
INPUT_SWITCH_PATH = UPPER_PANEL_PATH / "input_switch"
OUTPUT_SWITCH_PATH = UPPER_PANEL_PATH / "output_switch"
INPUT_POWER_LABEL_PATH = UPPER_PANEL_PATH / "input_power"
OUTPUT_POWER_LABEL_PATH = UPPER_PANEL_PATH / "output_power"
CLOSE_BTN_PATH = UPPER_PANEL_PATH / "close_btn"
IO_SETTINGS_PATH = LOWER_PANEL_PATH / "io_settings"

FACE_BTN_NAMES = (
    "bottom_set_btn",
    "top_set_btn",
    "north_set_btn",
    "south_set_btn",
    "west_set_btn",
    "east_set_btn",
)
FACE_KEYS = ("bottom", "top", "north", "south", "west", "east")
DEFAULT_IO_MODES = {
    "bottom": IOModes.OUTPUT,
    "top": IOModes.INPUT,
    "north": IOModes.OUTPUT,
    "south": IOModes.OUTPUT,
    "west": IOModes.OUTPUT,
    "east": IOModes.OUTPUT,
}


@RegistToolDeltaScreen("EnergyCubeUI.main", key=ENERGY_CUBE_UI)
class EnergyCubeUI(MachinePanelUI):
    EXIT_BTN_PATH = CLOSE_BTN_PATH
    allow_esc_exit = True

    def OnCreate(self):
        self.energy_label = self.GetElement(ENERGY_LABEL_PATH).asLabel()
        self.total_power = self.GetElement(TOTAL_POWER_PATH).asLabel()
        self.battery_icon = self.GetElement(BATTERY_ICON_PATH)
        self.input_switch = self.GetElement(INPUT_SWITCH_PATH).asSwitch()
        self.output_switch = self.GetElement(OUTPUT_SWITCH_PATH).asSwitch()
        self.input_power_label = self.GetElement(INPUT_POWER_LABEL_PATH).asLabel()
        self.output_power_label = self.GetElement(OUTPUT_POWER_LABEL_PATH).asLabel()
        self.io_settings = self.GetElement(IO_SETTINGS_PATH)
        self.io_mode_btns = []  # type: list[UBaseCtrl]
        self.io_modes = [DEFAULT_IO_MODES[face_key] for face_key in FACE_KEYS]
        for face, btn_name in enumerate(FACE_BTN_NAMES):
            btn = (
                self.io_settings[btn_name]
                .asButton()
                .SetCallback(lambda _, face=face: self.switch_io_mode(face))
            )
            self.io_mode_btns.append(btn)
        self.refresh_io_mode_btns()

    def OnTicking(self):
        if not self.inited:
            return
        data = GetBlockEntityData(self.x, self.y, self.z)
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        input_power = GetValue(data, K_INPUT_POWER, 0)
        output_power = GetValue(data, K_OUTPUT_POWER, 0)

        self.input_power_label.SetText("输入 %s/t" % FormatRF(input_power))
        self.output_power_label.SetText("输出 %s/t" % FormatRF(output_power))
        self.energy_label.SetText(
            "{:.1f}%%".format(float(store_rf * 100) / STORE_RF_MAX)
        )
        self.total_power.SetText(
            "%s / %s" % (FormatRF(store_rf), FormatRF(STORE_RF_MAX))
        )
        UpdateGenericProgressL2R(self.battery_icon, float(store_rf) / STORE_RF_MAX)

    @MachinePanelUI.Listen(EnergyCubeStatesUpdate)
    def onStateUpdate(self, event):
        # type: (EnergyCubeStatesUpdate) -> None
        self.input_switch.SetState(event.enable_input)
        self.output_switch.SetState(event.enable_output)

    @Binder.binding(Binder.BF_ToggleChanged, "#EnergyCubeUI.input_switch")
    def onInputSwitchChanged(self, args):
        EnergyCubeActionRequest(
            self.x,
            self.y,
            self.z,
            EnergyCubeActionRequest.OPERATION_INPUT,
            args["state"],
        ).send()

    @Binder.binding(Binder.BF_ToggleChanged, "#EnergyCubeUI.output_switch")
    def onOutputSwitchChanged(self, args):
        EnergyCubeActionRequest(
            self.x,
            self.y,
            self.z,
            EnergyCubeActionRequest.OPERATION_OUTPUT,
            args["state"],
        ).send()

    def switch_io_mode(self, face):
        # type: (int) -> None
        next_mode = (
            IOModes.OUTPUT if self.io_modes[face] == IOModes.INPUT else IOModes.INPUT
        )
        self.io_modes[face] = next_mode
        EnergyCubeSetIOModes(self.x, self.y, self.z, face, next_mode).send()
        self.update_io_mode_btn(face, next_mode)

    def refresh_io_mode_btns(self, data=None):
        # type: (dict | None) -> None
        if data is None:
            raw = GetBlockEntityData(self.x, self.y, self.z)
            if raw is None:
                self.update_all_io_mode_btns()
                return
            data = raw["exData"]
        self.io_modes = self._read_io_modes(data)
        self.update_all_io_mode_btns()

    def _read_io_modes(self, data):
        # type: (dict) -> list[int]
        raw_modes = NBT2Py(data.get(K_IO_MODE, {})) or {}
        if not isinstance(raw_modes, dict):
            raw_modes = {}
        modes = []
        for face_key in FACE_KEYS:
            mode = raw_modes.get(face_key, DEFAULT_IO_MODES[face_key])
            try:
                mode = int(mode)
            except (TypeError, ValueError):
                mode = DEFAULT_IO_MODES[face_key]
            if mode not in (IOModes.INPUT, IOModes.OUTPUT):
                mode = DEFAULT_IO_MODES[face_key]
            modes.append(mode)
        return modes

    def update_all_io_mode_btns(self):
        for face, mode in enumerate(self.io_modes):
            self.update_io_mode_btn(face, mode)

    def update_io_mode_btn(self, face, io_mode):
        # type: (int, int) -> None
        if io_mode:
            uv_start = (0, 4)
        else:
            uv_start = (0, 0)
        btn = self.io_mode_btns[face]
        btn["icon"].asImage().SetUV(uv_start, (4, 4))
        btn["io_tip"].asLabel().SetText(
            {
                IOModes.INPUT: "§4输入",
                IOModes.OUTPUT: "§9输出",
            }.get(io_mode, "--")
        )
