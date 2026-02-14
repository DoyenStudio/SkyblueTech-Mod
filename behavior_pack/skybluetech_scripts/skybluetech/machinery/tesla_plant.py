# coding=utf-8

from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerBlockUseEvent,
)
from ..define import flags
from ..define.id_enum.machinery import TESLA_PLANT as MACHINE_ID
from ..ui_sync.machinery.tesla_plant import TeslaPlantUISync
from .basic import (
    AutoSaver,
    ItemContainer,
    GUIControl,
    SPControl,
    WorkRenderer,
    RegisterMachine,
)

K_SETTING_ATTACK_MOB = "st:do_attack_mob"
K_SETTING_ATTACK_PLAYER = "st:do_attack_player"
K_SETTING_ENABLE = "st:do_enable"
K_SETTING_WORK_RANGE = "st:work_range"


@RegisterMachine
class TeslaPlant(AutoSaver, GUIControl, ItemContainer, SPControl, WorkRenderer):
    block_name = MACHINE_ID

    def __init__(self, dim, x, y, z, block_entity_data):
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        SPControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = TeslaPlantUISync.NewServer(self).Activate()

    def OnLoad(self):
        SPControl.OnLoad(self)
        self.work_range = self.bdata[K_SETTING_WORK_RANGE] or 5
        self.do_enable = self.bdata[K_SETTING_ENABLE] or False
        self.do_attack_player = self.bdata[K_SETTING_ATTACK_PLAYER] or False
        self.do_attack_mob = self.bdata[K_SETTING_ATTACK_MOB] or True

    def OnClick(self, event, extra_datas):
        GUIControl.OnClick(self, event, extra_datas)

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    def Dump(self):
        SPControl.Dump(self)
        self.bdata[K_SETTING_ENABLE] = self.do_enable
        self.bdata[K_SETTING_ATTACK_PLAYER] = self.do_attack_player
        self.bdata[K_SETTING_ATTACK_MOB] = self.do_attack_mob
        self.bdata[K_SETTING_WORK_RANGE] = self.work_range

    def OnUnload(self):
        AutoSaver.OnUnload(self)
        GUIControl.OnUnload(self)

    def SetDeactiveFlag(self, flag):
        SPControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def attack_once(self):
        pass
