# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.digger import (
    K_FRONT_BLOCK_AUX,
    K_FRONT_BLOCK_ID,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdateGenericProgressL2R, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
BLOCK_DISP_PATH = MAIN_PATH / "block_disp"
WORK_STATUS_PATH = MAIN_PATH / "work_status"


@RegistToolDeltaScreen("DiggerUI.main", is_proxy=True)
class DiggerUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPageIndirectional,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.block_disp = self.GetElement(BLOCK_DISP_PATH).asItemRenderer()
        self.work_status = self.GetElement(WORK_STATUS_PATH).asLabel()
        self.block_disp.SetUiItem(Item("minecraft:barrier"))

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        storage_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        front_block_id = GetValue(data, K_FRONT_BLOCK_ID, None)
        front_block_aux = GetValue(data, K_FRONT_BLOCK_AUX, 0)
        UpdatePowerBar(self.power_bar, storage_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        if front_block_id == "minecraft:air" or front_block_id is None:
            front_block_id = "minecraft:barrier"
        self.block_disp.SetUiItem(Item(front_block_id, front_block_aux))
        if front_block_id != "minecraft:barrier":
            self.work_status.SetText("当前正在挖掘 " + GetItemHoverName(front_block_id))
        else:
            self.work_status.SetText("当前无可挖掘方块")
