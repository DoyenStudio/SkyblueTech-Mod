# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ..basic import BaseMachine
from ..basic.register import BaseMachine, RegisterMachine

from ...define.machine_config import (
    fermenter
)


REG_BLOCK_IDS = (
    fermenter.IO_ENERGY,
)


@RegisterMachine
class EnergyInputInterface(BaseMachine):
    store_rf_max = 1
    extra_block_names = REG_BLOCK_IDS

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.machine_ref = None # type: ref[BaseMachine] | None

    def getMachineRef(self):
        # type: () -> BaseMachine | None
        if self.machine_ref is None:
            return None
        return self.machine_ref()

    def SetMachineRef(self, machine):
        # type: (BaseMachine) -> None
        self.machine_ref = ref(machine)

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
        # type: (int, bool, int | None, int) -> tuple[bool, int]
        m = self.getMachineRef()
        if m is None:
            return False, rf
        else:
            return m.AddPower(rf, is_generator, max_limit, depth)

