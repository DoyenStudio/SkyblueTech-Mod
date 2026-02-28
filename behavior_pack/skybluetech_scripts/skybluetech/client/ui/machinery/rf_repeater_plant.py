# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl
from ....common.define.ui_keys import RF_REPEATER_PLANT_UI
from ....common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantSettingUpload,
    RFRepeaterPlantSettingsUpdate,
)
from ....common.ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ..misc.rf_repeater_plant_build import RFRepeaterPlantBuildUI
from .define import MachinePanelUI, SCREEN_BASE_PATH

DATABOARD_NODE = SCREEN_BASE_PATH / "databoard/label"
IOTIPS_NODE = SCREEN_BASE_PATH / "energy_io_modes_disp"
BUILD_BTN_NODE = SCREEN_BASE_PATH / "build_btn"
CTRLS_NODE = SCREEN_BASE_PATH / "energy_io_ctrls"
CTRL_NORTH_NODE = CTRLS_NODE / "north_ctrl"
CTRL_SOUTH_NODE = CTRLS_NODE / "south_ctrl"
CTRL_EAST_NODE = CTRLS_NODE / "east_ctrl"
CTRL_WEST_NODE = CTRLS_NODE / "west_ctrl"


@RegistToolDeltaScreen("RFRepeaterPlantUI.main", key=RF_REPEATER_PLANT_UI)
class RFRepeaterPlantUI(MachinePanelUI):
    EXIT_BTN_PATH = SCREEN_BASE_PATH / "close_btn"
    allow_esc_exit = True

    def OnCreate(self):
        self.databoard = self.GetElement(DATABOARD_NODE).asLabel()
        self.io_tips = self.GetElement(IOTIPS_NODE).asLabel()
        self.build_btn = (
            self
            .GetElement(BUILD_BTN_NODE)
            .asButton()
            .SetCallback(self.on_press_build_btn)
        )
        self.north_ctrl_btn = (
            self
            .GetElement(CTRL_NORTH_NODE)
            .asButton()
            .SetCallback(self.on_press_north_ctrl)
        )
        self.south_ctrl_btn = (
            self
            .GetElement(CTRL_SOUTH_NODE)
            .asButton()
            .SetCallback(self.on_press_south_ctrl)
        )
        self.east_ctrl_btn = (
            self
            .GetElement(CTRL_EAST_NODE)
            .asButton()
            .SetCallback(self.on_press_east_ctrl)
        )
        self.west_ctrl_btn = (
            self
            .GetElement(CTRL_WEST_NODE)
            .asButton()
            .SetCallback(self.on_press_west_ctrl)
        )
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
        set_ctrl_button_tipimg(self.east_ctrl_btn, event.east_io_mode)
        set_ctrl_button_tipimg(self.west_ctrl_btn, event.west_io_mode)
        set_ctrl_button_tipimg(self.north_ctrl_btn, event.north_io_mode)
        set_ctrl_button_tipimg(self.south_ctrl_btn, event.south_io_mode)
        self.databoard.SetText(
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
        self.curr_north_ctrl_mode = event.north_io_mode
        self.curr_south_ctrl_mode = event.south_io_mode
        self.curr_east_ctrl_mode = event.east_io_mode
        self.curr_west_ctrl_mode = event.west_io_mode
        self.io_tips.SetText(
            "§5E (x+)： %s\n§tW (x-)： %s\n§9S (z+)： %s\n§4N (z-)： %s"
            % (
                mode2str(self.curr_east_ctrl_mode),
                mode2str(self.curr_west_ctrl_mode),
                mode2str(self.curr_south_ctrl_mode),
                mode2str(self.curr_north_ctrl_mode),
            )
        )

    def on_press_build_btn(self, _):
        self.RemoveUI()
        RFRepeaterPlantBuildUI.CreateUI({
            "pos": (self.x, self.y, self.z),
            "isHud": True,
        })

    def on_press_north_ctrl(self, _):
        self.curr_north_ctrl_mode = not self.curr_north_ctrl_mode
        RFRepeaterPlantSettingUpload(
            self.x,
            self.y,
            self.z,
            RFRepeaterPlantSettingUpload.IO_NORTH,
            self.curr_north_ctrl_mode,
        ).send()
        set_ctrl_button_tipimg(self.north_ctrl_btn, self.curr_north_ctrl_mode)

    def on_press_south_ctrl(self, _):
        self.curr_south_ctrl_mode = not self.curr_south_ctrl_mode
        RFRepeaterPlantSettingUpload(
            self.x,
            self.y,
            self.z,
            RFRepeaterPlantSettingUpload.IO_SOUTH,
            self.curr_south_ctrl_mode,
        ).send()
        set_ctrl_button_tipimg(self.south_ctrl_btn, self.curr_south_ctrl_mode)

    def on_press_east_ctrl(self, _):
        self.curr_east_ctrl_mode = not self.curr_east_ctrl_mode
        RFRepeaterPlantSettingUpload(
            self.x,
            self.y,
            self.z,
            RFRepeaterPlantSettingUpload.IO_EAST,
            self.curr_east_ctrl_mode,
        ).send()
        set_ctrl_button_tipimg(self.east_ctrl_btn, self.curr_east_ctrl_mode)

    def on_press_west_ctrl(self, _):
        self.curr_west_ctrl_mode = not self.curr_west_ctrl_mode
        RFRepeaterPlantSettingUpload(
            self.x,
            self.y,
            self.z,
            RFRepeaterPlantSettingUpload.IO_WEST,
            self.curr_west_ctrl_mode,
        ).send()
        set_ctrl_button_tipimg(self.west_ctrl_btn, self.curr_west_ctrl_mode)


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
    # type: (UBaseCtrl, bool) -> None
    if mode:
        # mode=output=True=green
        ctrl["arrow"].asImage().SetUV((0, 16), (16, 16))
    else:
        # mode=input=False=red
        ctrl["arrow"].asImage().SetUV((0, 0), (16, 16))
