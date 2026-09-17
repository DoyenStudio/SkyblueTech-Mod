# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.ui_keys import REDSTONEFLUX_BRAKE_UI
from skybluetech_scripts.skybluetech.common.events.machinery.redstoneflux_brake import (
    RedstoneFluxBrakeModeSwitchRequest,
)
from skybluetech_scripts.skybluetech.common.machinery_def.redstoneflux_brake import (
    K_ENABLE,
    K_INVERT_REDSTONE,
    K_POWER_AVG,
    K_REDSTONE_STRENGTH,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import (
    SCREEN_BASE_PATH,
    Binder,
    RegistToolDeltaScreen,
)
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MachinePanelUI
from .utils import FormatRF

POWER_AVG_LABEL_PATH = SCREEN_BASE_PATH / "power_board/label"
ENERGY_SCROLL_PATH = SCREEN_BASE_PATH / "graphics/wire/energy_scroll"
REDSTONE_WIRE_PATH = SCREEN_BASE_PATH / "graphics/redstone_wire"
REDSTONE_MODE_SWITCH_PATH = SCREEN_BASE_PATH / "redstone_mode_switch"


@RegistToolDeltaScreen("RedstoneFluxBrakeUI.main", key=REDSTONEFLUX_BRAKE_UI)
class RedstoneFluxBrakeUI(MachinePanelUI):
    allow_esc_exit = True
    EXIT_BTN_PATH = SCREEN_BASE_PATH / "close_btn"

    def OnCreate(self):
        self.power_avg = 0
        self.power_avg_label = self.GetElement(POWER_AVG_LABEL_PATH).asLabel()
        self.energy_scroll = self.GetElement(ENERGY_SCROLL_PATH)
        self.energy_scroll_base_pos = self.energy_scroll.GetPos()
        self.energy_scroll_offset = 0
        self.redstone_wire = self.GetElement(REDSTONE_WIRE_PATH).asImage()
        self.redstone_mode_switch = self.GetElement(REDSTONE_MODE_SWITCH_PATH).asSwitch()
        self.invert_redstone = False

    def OnTicking(self):
        if not self.inited:
            return
        data = GetBlockEntityData(self.x, self.y, self.z)
        if data is None:
            return
        data = data["exData"]
        invert_redstone = GetValue(data, K_INVERT_REDSTONE, False)
        if invert_redstone != self.invert_redstone:
            self.invert_redstone = invert_redstone
            self.redstone_mode_switch.SetState(invert_redstone)
        if GetValue(data, K_ENABLE, False):
            self.energy_scroll_offset = (self.energy_scroll_offset + 1) % 16
            self.energy_scroll.SetPos((
                self.energy_scroll_base_pos[0] + self.energy_scroll_offset,
                self.energy_scroll_base_pos[1],
            ))
        redstone_strength = GetValue(data, K_REDSTONE_STRENGTH, 0)
        redstone_strength = min(15, max(0, redstone_strength))
        redstone_r = (0x40 + (0xFF - 0x40) * redstone_strength / 15.0) / 255.0
        self.redstone_wire.SetSpriteColor((redstone_r, 0, 0))
        self.power_avg = GetValue(data, K_POWER_AVG, 0)
        self.power_avg_label.SetText("%s/s" % FormatRF(self.power_avg))

    @Binder.binding(Binder.BF_ToggleChanged, "#RedstoneFluxBrakeUI.redstone_mode_switch")
    def onRedstoneModeSwitchChanged(self, args):
        # type: (dict) -> None
        RedstoneFluxBrakeModeSwitchRequest(
            self.x, self.y, self.z, args["state"]
        ).send()
