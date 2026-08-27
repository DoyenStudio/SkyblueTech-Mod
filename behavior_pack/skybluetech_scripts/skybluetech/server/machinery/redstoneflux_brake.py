# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockNeighborChangedServerEvent,
    BlockStrengthChangedServerEvent,
    ServerBlockUseEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum.machinery import Machinery
from ...common.define.ui_keys import REDSTONEFLUX_BRAKE_UI
from ...common.events.machinery.redstoneflux_brake import (
    RedstoneFluxBrakeModeSwitchRequest,
)
from ...common.machinery_def.redstoneflux_brake import (
    K_ENABLE,
    K_INVERT_REDSTONE,
    K_POWER_AVG,
    K_REDSTONE_STRENGTH,
)
from ..transmitters.wire.logic import logic_module
from .basic import (
    BaseClicker,
    BasePowerProvider,
    GUIControl,
    OperationListener,
    RegisterMachine,
)


@RegisterMachine
class RedstonefluxBrake(BaseClicker, BasePowerProvider, GUIControl, OperationListener):
    bound_ui = REDSTONEFLUX_BRAKE_UI
    block_name = Machinery.REDSTONEFLUX_BRAKE

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._invert_redstone = self.bdata[K_INVERT_REDSTONE] or False
        self.power_avg = self.bdata[K_POWER_AVG] or 0
        self._redstone_strength = self.bdata[K_REDSTONE_STRENGTH] or 0
        self._enabled = self.calc_enabled_by_redstone()
        self.bdata[K_ENABLE] = self._enabled
        if not self._enabled:
            self.power_avg = 0
            self.bdata[K_POWER_AVG] = 0
        self.t = 0
        ExecLater(0, self.update_stat)

    def OnTicking(self):
        self.t += 1
        if self.t >= 20:
            self.t = 0
            if self.enabled:
                self.power_avg = sum(i.power_through_avg for i in self.get_networks())
            else:
                self.power_avg = 0
            self.bdata[K_POWER_AVG] = self.power_avg

    def OnClick(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        GUIControl.OnClick(self, event)

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        self.update_stat()

    def OnBlockRedstoneStrengthChanged(self, event):
        # type: (BlockStrengthChangedServerEvent) -> None
        self.redstone_strength = event.newStrength
        self.update_enabled_by_redstone()

    def get_networks(self):
        cnode = logic_module.GetContainerNode(self.dim, self.x, self.y, self.z)
        return list(cnode.get_inputs().values()) + list(cnode.get_outputs().values())

    def update_stat(self):
        networks = self.get_networks()
        for network in networks:
            network.enabled = self.enabled

    def calc_enabled_by_redstone(self):
        # type: () -> bool
        has_signal = self.redstone_strength > 0
        return has_signal != self.invert_redstone

    def update_enabled_by_redstone(self):
        # type: () -> None
        self.enabled = self.calc_enabled_by_redstone()

    @property
    def enabled(self):
        # type: () -> bool
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        # type: (bool) -> None
        if value == self._enabled:
            return
        self._enabled = value
        self.bdata[K_ENABLE] = value
        if not value:
            self.power_avg = 0
            self.bdata[K_POWER_AVG] = 0
        self.update_stat()

    @property
    def redstone_strength(self):
        # type: () -> int
        return self._redstone_strength

    @redstone_strength.setter
    def redstone_strength(self, value):
        # type: (int) -> None
        self._redstone_strength = value
        self.bdata[K_REDSTONE_STRENGTH] = value

    @property
    def invert_redstone(self):
        # type: () -> bool
        return self._invert_redstone

    @invert_redstone.setter
    def invert_redstone(self, value):
        # type: (bool) -> None
        if value == self._invert_redstone:
            return
        self._invert_redstone = value
        self.bdata[K_INVERT_REDSTONE] = value
        self.update_enabled_by_redstone()


@RedstonefluxBrake.ForOperation(RedstoneFluxBrakeModeSwitchRequest)
def onRedstoneFluxBrakeModeSwitch(event, machine):
    # type: (RedstoneFluxBrakeModeSwitchRequest, RedstonefluxBrake) -> None
    machine.invert_redstone = event.invert_redstone
