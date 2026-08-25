# coding=utf-8

from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.server import UpdateBlockStates
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.facing import FACING_DXYZ, OPPOSITE_FACING
from ...common.define.id_enum import Machinery
from ...common.define.ui_keys import ENERGY_CUBE_UI
from ...common.events.machinery.energy_cube import (
    EnergyCubeActionRequest,
    EnergyCubeSetIOModes,
    EnergyCubeStatesUpdate,
)
from ...common.machinery_def.energy_cube import (
    K_ENABLE_INPUT,
    K_ENABLE_OUTPUT,
    K_INPUT_POWER,
    K_OUTPUT_POWER,
    MAX_INPUT_POWER,
    MAX_OUTPUT_POWER,
    STORE_RF_MAX,
    EnergyIOMode,
    IOModes,
)
from .basic import (
    BaseClicker,
    BasePowerProvider,
    GUIControl,
    OperationListener,
    RegisterMachine,
)


@RegisterMachine
class EnergyCubeJunior(BaseClicker, BasePowerProvider, GUIControl, OperationListener):
    block_name = Machinery.ENERGY_CUBE_JUNIOR
    bound_ui = ENERGY_CUBE_UI
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (0, 0, 0, 0, 0, 0)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.io_modes = IOModes(block_entity_data)
        self.energy_io_mode = self.io_modes.modes()
        self._refresh_output_faces()
        self._last_rf_provided = 0
        self._input_sum = 0
        self._output_sum = 0
        self._power_sample_ticks = 0
        self.bdata[K_INPUT_POWER] = 0.0
        self.bdata[K_OUTPUT_POWER] = 0.0

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        if (
            self.enable_output
            and self.store_rf > 0
            and self._power_output_faces
        ):
            output_rf = min(int(self.store_rf), MAX_OUTPUT_POWER)
            remaining = self._output_nearby(output_rf)[1]
            transferred = output_rf - remaining
            if transferred > 0:
                self.store_rf -= transferred
                self._output_sum += transferred

        self._power_sample_ticks += 1
        if self._power_sample_ticks < 20:
            return
        self.bdata[K_INPUT_POWER] = self._input_sum * 1.0 / self._power_sample_ticks
        self.bdata[K_OUTPUT_POWER] = self._output_sum * 1.0 / self._power_sample_ticks
        self._input_sum = 0
        self._output_sum = 0
        self._power_sample_ticks = 0
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnClick(self, event, extra_datas=None):
        ExecLater(
            0.1,
            lambda: EnergyCubeStatesUpdate(
                self.enable_input, self.enable_output
            ).send(event.playerId),
        )

    def OnPlaced(self, event):
        UpdateBlockStates(self.dim, (self.x, self.y, self.z), self.io_modes.states())

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def AddPower(self, rf):
        if not self.enable_input:
            return False, rf
        in_rf = min(MAX_INPUT_POWER*5, rf) # 每 5t 线缆取走一次能量
        in_rf_overflow = rf - in_rf
        ok, in_rf_overflow_2 = BasePowerProvider.AddPower(self, in_rf)
        self._input_sum += in_rf - in_rf_overflow_2
        return ok, in_rf_overflow + in_rf_overflow_2

    def TakeoutPower(self, rf):
        if not self.enable_output:
            return 0
        rf_takeout = min(rf, MAX_OUTPUT_POWER*5) # 每 5t 线缆取走一次能量
        self._last_rf_provided = BasePowerProvider.TakeoutPower(self, rf_takeout)
        return self._last_rf_provided

    def GivebackPower(self, rf):
        BasePowerProvider.GivebackPower(self, rf)
        self._output_sum += self._last_rf_provided - rf
        self._last_rf_provided = 0

    def OnDestroy(self):
        pass

    def set_io_mode(self, face, io_mode):
        # type: (int, int) -> None
        self.io_modes._modes[face] = io_mode
        self.io_modes.save()
        self.energy_io_mode = self.io_modes.modes()
        self._refresh_output_faces()
        UpdateBlockStates(
            self.dim, (self.x, self.y, self.z), self.io_modes.states()
        )
        self.update_neighbor_access_point_modes()

    def _refresh_output_faces(self):
        self._power_output_faces = tuple(
            i for i, mode in enumerate(self.energy_io_mode)
            if mode == EnergyIOMode.OUTPUT
        )
        self._output_neighbors_cache = None

    def set_enable_input(self, value):
        # type: (bool) -> None
        if isinstance(value, bool):
            self.enable_input = value

    def set_enable_output(self, value):
        # type: (bool) -> None
        if isinstance(value, bool):
            self.enable_output = value

    @property
    def enable_input(self):
        # type: () -> bool
        value = self.bdata[K_ENABLE_INPUT]
        if value is None:
            self.bdata[K_ENABLE_INPUT] = value = True
        return value

    @enable_input.setter
    def enable_input(self, value):
        # type: (bool) -> None
        self.bdata[K_ENABLE_INPUT] = value

    @property
    def enable_output(self):
        # type: () -> bool
        value = self.bdata[K_ENABLE_OUTPUT]
        if value is None:
            self.bdata[K_ENABLE_OUTPUT] = value = True
        return value

    @enable_output.setter
    def enable_output(self, value):
        # type: (bool) -> None
        self.bdata[K_ENABLE_OUTPUT] = value

    def update_neighbor_access_point_modes(self):
        from ..transmitters.base.define import AP_MODE_INPUT, AP_MODE_OUTPUT
        from ..transmitters.wire.logic import logic_module

        for face, (dx, dy, dz) in enumerate(FACING_DXYZ):
            ap = logic_module.access_points_pool.get(
                (
                    self.dim,
                    self.x + dx,
                    self.y + dy,
                    self.z + dz,
                    OPPOSITE_FACING[face],
                )
            )
            if ap is None:
                continue
            res = logic_module.SetAccessPointIOMode(
                ap,
                {
                    EnergyIOMode.INPUT: AP_MODE_INPUT,
                    EnergyIOMode.OUTPUT: AP_MODE_OUTPUT,
                }[self.io_modes._modes[face]],
            )
            if not res:
                print("[Error] EnergyCube: set node io mode failed")


@EnergyCubeJunior.ForOperation(EnergyCubeSetIOModes)
def onSetModes(event, machine):
    # type: (EnergyCubeSetIOModes, EnergyCubeJunior) -> None
    if event.face not in {0, 1, 2, 3, 4, 5} or event.mode not in {0, 1}:
        return
    machine.set_io_mode(event.face, event.mode)


@EnergyCubeJunior.ForOperation(EnergyCubeActionRequest)
def onActionRequest(event, machine):
    # type: (EnergyCubeActionRequest, EnergyCubeJunior) -> None
    if event.op == event.OPERATION_INPUT:
        machine.set_enable_input(event.value)
    elif event.op == event.OPERATION_OUTPUT:
        machine.set_enable_output(event.value)
    else:
        return
    machine.CallSync()
