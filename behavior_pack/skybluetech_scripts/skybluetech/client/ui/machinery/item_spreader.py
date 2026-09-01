# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.item_spreader import (
    K_NUM_CONTAINERS,
    K_SPREADER_POINTER,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PROGRESS_PATH = MAIN_PATH / "progress"
NOTE_LABEL_PATH = MAIN_PATH / "note_label"


@RegistToolDeltaScreen("ItemSpreaderUI.main", is_proxy=True)
class ItemSpreaderUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PROGRESS_PATH)
        self.note_label = self.GetElement(NOTE_LABEL_PATH).asLabel()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        num_containers = GetValue(data, K_NUM_CONTAINERS, 0)
        spreader_pointer = GetValue(data, K_SPREADER_POINTER, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        if num_containers > 0:
            spreader_pointer %= num_containers
            display_pointer = spreader_pointer + 1
            progress = float(spreader_pointer + 1) / num_containers
        else:
            display_pointer = 0
            progress = 0.0
        self.note_label.SetText(
            "正在投递第 %d / %d 个容器" % (display_pointer, num_containers)
        )
        self.progress["mask"].SetFullSize(
            "x", UICtrlPosData("parent", relative_value=progress)
        )
