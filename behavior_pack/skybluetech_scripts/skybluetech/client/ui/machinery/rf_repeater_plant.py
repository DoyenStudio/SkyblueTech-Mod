# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl
from ....common.define.ui_keys import RF_REPEATER_PLANT_UI
from ....common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantSettingUpload,
    RFRepeaterPlantSettingsUpdate,
)
from ....common.machinery_def.rf_repeater_plant import reverse_mode
from ....common.ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ..misc.rf_repeater_plant_build import RFRepeaterPlantBuildUI
from .define import MachinePanelUI, SCREEN_BASE_PATH

DATABOARD_TIP_TEXT_NODE = SCREEN_BASE_PATH / "databoard/tip_text"
IO_MODE_CTRL_NODE = SCREEN_BASE_PATH / "io_mode_ctrl"
BUILD_BTN_NODE = SCREEN_BASE_PATH / "build_btn"
IO_CTRL_BTN_NODE = IO_MODE_CTRL_NODE / "io_ctrl_btn"
IO_MODE_LABEL_NODE = IO_MODE_CTRL_NODE / "io_mode_label"


@RegistToolDeltaScreen("RFRepeaterPlantUI.main", key=RF_REPEATER_PLANT_UI)
class RFRepeaterPlantUI(MachinePanelUI):
    EXIT_BTN_PATH = SCREEN_BASE_PATH / "close_btn"
    allow_esc_exit = True

    def OnCreate(self):
        self.io_tips = self.GetElement(DATABOARD_TIP_TEXT_NODE).asLabel()
        self.build_btn = (
            self
            .GetElement(BUILD_BTN_NODE)
            .asButton()
            .SetCallback(self.on_press_build_btn)
        )
        self.io_ctrl_btn = (
            self
            .GetElement(IO_CTRL_BTN_NODE)
            .asButton()
            .SetCallback(self.on_press_io_ctrl_btn)
        )
        self.io_mode_label = self.GetElement(IO_MODE_LABEL_NODE).asLabel()
        self.onContentUpdate(
            RFRepeaterPlantSettingsUpdate.unmarshal(
                self._init_params["st:init_content"]
            )
        )
        self.sync = RFRepeaterPlantUISync.NewClient(
            self.dim, self.x, self.y, self.z
        ).Activate()

    @MachinePanelUI.Listen(RFRepeaterPlantSettingsUpdate)
    def onContentUpdate(self, event):
        # type: (RFRepeaterPlantSettingsUpdate) -> None
        set_ctrl_button_tipimg(self.io_ctrl_btn, event.io_mode)
        self.io_tips.SetText(
            format_content(
                event.network_euid,
                event.network_plant_count,
                event.network_plant_online_count,
                event.total_output_count,
                event.total_output_active_count,
                event.total_input_count,
                event.total_input_active_count,
            )
        )
        self.current_io_mode = event.io_mode
        if self.current_io_mode:
            self.io_mode_label.SetText("§4中继塔向电网供能")
        else:
            self.io_mode_label.SetText("§2电网向中继塔供能")

    def on_press_build_btn(self, _):
        self.RemoveUI()
        RFRepeaterPlantBuildUI.CreateUI({
            "pos": (self.x, self.y, self.z),
            "isHud": True,
        })

    def on_press_io_ctrl_btn(self, _):
        self.current_io_mode = reverse_mode(self.current_io_mode)
        RFRepeaterPlantSettingUpload(
            self.x,
            self.y,
            self.z,
            self.current_io_mode,
        ).send()
        set_ctrl_button_tipimg(self.io_ctrl_btn, self.current_io_mode)


def mode2str(m):
    # type: (bool) -> str
    return "§4输出" if m else "§a输入"


def format_content(
    network_euid,  # type: str
    network_plant_count,  # type: int
    network_plant_online_count,  # type: int
    total_output_count,  # type: int
    total_output_active_count,  # type: int
    total_input_count,  # type: int
    total_input_active_count,  # type: int
):
    return (
        "§a[%s] 电网架设完毕。"
        "\n"
        "\n§b电网中继塔数： §f%d （在线 %d）"
        "\n§4总输出端数： §f%d （在线 %d）"
        "\n§a总输入端数： §f%d （在线 %d）"
    ) % (
        network_euid.upper(),
        network_plant_count,
        network_plant_online_count,
        total_output_count,
        total_output_active_count,
        total_input_count,
        total_input_active_count,
    )


def set_ctrl_button_tipimg(ctrl, mode):
    # type: (UBaseCtrl, int) -> None
    if mode:
        ctrl["arrow"].asImage().SetUV((16, 0), (16, 16))
    else:
        ctrl["arrow"].asImage().SetUV((0, 0), (16, 16))
