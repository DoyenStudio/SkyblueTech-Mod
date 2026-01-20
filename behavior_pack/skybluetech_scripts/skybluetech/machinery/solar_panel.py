# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.api.server import (
    GetTopBlockHeight,
    GetLocalTime,
    IsRaining,
    UpdateBlockStates,
    GetBlockName,
)
from ..define.id_enum.machinery import SOLAR_PANEL as MACHINE_ID
from ..define.facing import DXYZ_FACING, FACING_EN
from ..ui_sync.machinery.solar_panel import SolarPanelUISync
from ..transmitters.wire.logic import isWire
from .basic import AutoSaver, BasicGenerator, ItemContainer, GUIControl, RegisterMachine


@RegisterMachine
class SolarPanel(AutoSaver, BasicGenerator, ItemContainer, GUIControl):
    block_name = MACHINE_ID
    store_rf_max = 14400
    energy_io_mode = (1, 1, 1, 1, 1, 1)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BasicGenerator.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = SolarPanelUISync.NewServer(self).Activate()
        self.t = 0
        self.power_output = 0
        self.light_level = 0

    def OnTicking(self):
        self.t += 1
        if self.t >= 20:
            self.t = 0
            self.update()
        if self.t % 5 == 0 and self.IsActive():
            self.GeneratePower(self.power_output * 5)
            self.OnSync()

    def OnPlaced(self, _):
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isWire(bname)
            UpdateBlockStates(
                self.dim,
                (self.x, self.y, self.z),
                {"skybluetech:connection_" + facing_en: connectToWire},
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        connectToWire = isWire(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire},
        )

    def update(self):
        can_generate = GetTopBlockHeight((self.x, self.z), self.dim) == self.y
        localtime = GetLocalTime(self.dim) % 24000
        if IsRaining():
            self.light_level = GetSkylightLevelRain(localtime)
        else:
            self.light_level = GetSkylightLevelClear(localtime)
        if can_generate:
            self.power_output = round(self.light_level)
        else:
            self.power_output = 0
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.light_level = self.light_level
        self.sync.power = self.power_output
        self.sync.MarkedAsChanged()

    def OnUnload(self):
        # type: () -> None
        BasicGenerator.OnUnload(self)
        AutoSaver.OnUnload(self)
        GUIControl.OnUnload(self)


def GetSkylightLevelClear(time):
    # type: (int) -> int
    # 等级0
    if 13670 <= time <= 22330:
        return 0
    # 等级1
    elif 13219 <= time <= 13669 or 22331 <= time <= 22781:
        return 1
    # 等级2 - 仅BE：22782-23070
    elif 12931 <= time <= 13218 or 22782 <= time <= 23070:
        return 2
    # 等级3 - 仅BE：23071-23296
    elif 12705 <= time <= 12930 or 23071 <= time <= 23296:
        return 3
    # 等级4
    elif 12471 <= time <= 12704 or 23297 <= time <= 23529:
        return 4
    # 等级5
    elif 12233 <= time <= 12470 or 23530 <= time <= 23767:
        return 5
    # 等级6
    elif 12041 <= time <= 12232 or 23768 <= time <= 23960:
        return 6
    # 等级7 - 跨0点区间（23961-166）
    elif 11835 <= time <= 12040 or (23961 <= time <= 24000) or (0 <= time <= 166):
        return 7
    # 等级8 - 仅BE：11466-11834
    elif 11466 <= time <= 11834 or 167 <= time <= 535:
        return 8
    # 等级9 - 仅BE：11067-11465
    elif 11067 <= time <= 11465 or 536 <= time <= 933:
        return 9
    # 等级10
    elif 10629 <= time <= 11066 or 934 <= time <= 1371:
        return 10
    # 等级11
    elif 10136 <= time <= 10628 or 1372 <= time <= 1865:
        return 11
    # 等级12
    elif 9557 <= time <= 10135 or 1866 <= time <= 2444:
        return 12
    # 等级13
    elif 8826 <= time <= 9556 or 2445 <= time <= 3175:
        return 13
    # 等级14
    elif 7706 <= time <= 8825 or 3176 <= time <= 4294:
        return 14
    # 等级15
    elif 4295 <= time <= 7705:
        return 15
    # 异常时间值兜底
    else:
        return -1


def GetSkylightLevelRain(time):
    # type: (int) -> int
    # 等级0
    if 13670 <= time <= 22330:
        return 0
    # 等级1
    elif 13203 <= time <= 13669 or 22331 <= time <= 22798:
        return 1
    # 等级2 - 仅BE：时间↑ 12770-13202
    elif 12770 <= time <= 13202 or 22799 <= time <= 23231:
        return 2
    # 等级3 - 仅BE：时间↑ 12497-12769
    elif 12497 <= time <= 12769 or 23232 <= time <= 23504:
        return 3
    # 等级4
    elif 12256 <= time <= 12496 or 23505 <= time <= 23745:
        return 4
    # 等级5
    elif 12010 <= time <= 12255 or 23746 <= time <= 23991:
        return 5
    # 等级6 - 跨0点区间：23992-394 → 拆分为23992-24000 + 0-394
    elif 11607 <= time <= 12009 or (23992 <= time <= 24000) or (0 <= time <= 394):
        return 6
    # 等级7
    elif 11119 <= time <= 11606 or 395 <= time <= 882:
        return 7
    # 等级8 - 仅BE：时间↓ 883-1430
    elif 10571 <= time <= 11118 or 883 <= time <= 1430:
        return 8
    # 等级9 - 仅BE：时间↓ 1431-2069
    elif 9931 <= time <= 10570 or 1431 <= time <= 2069:
        return 9
    # 等级10 - 仅BE：时间↑ 9126-9930
    elif 9126 <= time <= 9930 or 2070 <= time <= 2875:
        return 10
    # 等级11 - 仅BE：时间↑ 7893-9125
    elif 7893 <= time <= 9125 or 2876 <= time <= 4108:
        return 11
    # 等级12 - 仅BE：时间↓ 4109-7892
    elif 4109 <= time <= 7892:
        return 12
    # 异常值/13级及以上（无数据）
    else:
        return -1
