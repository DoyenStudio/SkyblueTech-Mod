# coding=utf-8
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ..basic import BaseMachine


class BaseInterface(BaseMachine):
    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.machine_ref = None  # type: ref[BaseMachine] | None

    def getMachineRef(self):
        # type: () -> BaseMachine | None
        if self.machine_ref is None:
            return None
        return self.machine_ref()

    def SetMachineRef(self, machine):
        # type: (BaseMachine) -> None
        self.machine_ref = ref(machine)
