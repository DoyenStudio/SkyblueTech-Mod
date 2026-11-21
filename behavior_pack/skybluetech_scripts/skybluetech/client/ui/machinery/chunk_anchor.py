# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from ....common.events.machinery.chunk_anchor import ChunkAnchorRadiusRequest
from ....common.machinery_def.basic import K_STORE_RF
from ....common.machinery_def.chunk_anchor import (
    CAPACITY, RADIUS, STATUS, chunk_bounds, chunk_count,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar


@RegistToolDeltaScreen("ChunkAnchorUI.main", is_proxy=True)
class ChunkAnchorUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.bar = self.GetElement(MAIN_PATH / "power_bar")
        self.radius = self.GetElement(MAIN_PATH / "radius").asLabel()
        self.status = self.GetElement(MAIN_PATH / "status").asLabel()
        for name, step in (("minus", -1), ("plus", 1)):
            self.GetElement(MAIN_PATH / name).asButton().SetCallback(
                lambda _, step=step: self.adjust(step)
            )

    def adjust(self, step):
        _, x, y, z = self.pos
        ChunkAnchorRadiusRequest(x, y, z, step).send()

    def OnTicking(self):
        info = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:]) or {}
        data = info.get("exData") or {}
        radius = GetValueWithDefault(data, RADIUS, -1)
        rf = GetValueWithDefault(data, K_STORE_RF, 0)
        UpdatePowerBar(self.bar, rf, CAPACITY, hover="")
        text = "关闭"
        if radius >= 0:
            _, x, _, z = self.pos
            text = "半径 %d · %d 块" % (radius, chunk_count(chunk_bounds(radius, x, z)))
        self.radius.SetText(text)
        self.status.SetText(GetValueWithDefault(data, STATUS, "正在读取状态"))
