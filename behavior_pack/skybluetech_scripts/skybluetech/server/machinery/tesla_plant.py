# coding=utf-8

from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerBlockUseEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.id_enum.machinery import TESLA_PLANT as MACHINE_ID
from ...common.ui_sync.machinery.tesla_plant import TeslaPlantUISync
from .basic import (
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
class TeslaPlant(GUIControl, ItemContainer, SPControl, WorkRenderer):
    block_name = MACHINE_ID

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = TeslaPlantUISync.NewServer(self).Activate()
        self._cached_setting_do_enable = None
        self._cached_setting_do_attack_mob = None
        self._cached_setting_do_attack_player = None
        self._cached_work_range = None

    @SuperExecutorMeta.execute_super
    def OnClick(self, event, extra_datas):
        pass

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        pass

    def attack_once(self):
        pass

    @property
    def do_enable(self):
        # type: () -> bool
        if self._cached_setting_do_enable is None:
            self._cached_setting_do_enable = self.bdata[K_SETTING_ENABLE]
        return self._cached_setting_do_enable

    @do_enable.setter
    def do_enable(self, value):
        # type: (bool) -> None
        self._cached_setting_do_enable = self.bdata[K_SETTING_ENABLE] = value

    @property
    def do_attack_mob(self):
        # type: () -> bool
        if self._cached_setting_do_attack_mob is None:
            self._cached_setting_do_attack_mob = self.bdata[K_SETTING_ATTACK_MOB]
        return self._cached_setting_do_attack_mob

    @do_attack_mob.setter
    def do_attack_mob(self, value):
        # type: (bool) -> None
        self._cached_setting_do_attack_mob = self.bdata[K_SETTING_ATTACK_MOB] = value

    @property
    def do_attack_player(self):
        # type: () -> bool
        if self._cached_setting_do_attack_player is None:
            self._cached_setting_do_attack_player = self.bdata[K_SETTING_ATTACK_PLAYER]
        return self._cached_setting_do_attack_player

    @do_attack_player.setter
    def do_attack_player(self, value):
        # type: (bool) -> None
        self._cached_setting_do_attack_player = self.bdata[K_SETTING_ATTACK_PLAYER] = (
            value
        )

    @property
    def work_range(self):
        # type: () -> int
        if self._cached_work_range is None:
            self._cached_work_range = self.bdata[K_SETTING_WORK_RANGE] or 5
        return self._cached_work_range

    @work_range.setter
    def work_range(self, value):
        # type: (int) -> None
        self._cached_work_range = self.bdata[K_SETTING_WORK_RANGE] = value
