# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import (
    GetValueWithDefault as GetValue,
    ValueOf,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.mini_miner import (
    WorkMode,
    K_DIGGING_POS,
    K_WORK_MODE,
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
)
from ..machinery_extra_pages import (
    CableSettingsPageIndirectional,
    PipeSettingsPageIndirectional,
)
from .define_ex import MachinePanelUIProxyEx, MAIN_PATH
from .utils import UpdatePowerBar, FluidDisplayer

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"
INFO_LABEL_PATH = MAIN_PATH / "panel_bg/info_label"


@RegistToolDeltaScreen("MiniMinerUI.main", is_proxy=True)
class MiniMinerUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        CableSettingsPageIndirectional,
        PipeSettingsPageIndirectional,
    )

    def OnCreate(self):
        self.info_label = self.GetElement(INFO_LABEL_PATH).asLabel()
        self.power_bar = self.GetElement(POWER_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        fluid_id = GetValue(data, K_FLUID_ID, None)
        fluid_volume = GetValue(data, K_FLUID_VOLUME, 0)
        store_rf = GetValue(data, K_STORE_RF, 0)
        work_mode = GetValue(data, K_WORK_MODE, 0)
        digging_pos = GetValue(data, K_DIGGING_POS, [0, 0, 0])
        self.fluid_displayer.update(fluid_id, fluid_volume, MAX_FLUID_VOLUME)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        dx, dy, dz = digging_pos
        dx = ValueOf(dx)
        dy = ValueOf(dy)
        dz = ValueOf(dz)
        self.info_label.SetText(
            "正在挖掘： (%d, %d, %d)\n\n%s" % (dx, dy, dz, WorkMode.zh_cn(work_mode))
        )
