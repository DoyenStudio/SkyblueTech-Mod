# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ..basic import BasicGenerator
from ..basic.register import RegisterMachine

# LOADED_INTERFACES
#

REG_BLOCK_IDS = (   
)


@RegisterMachine
class EnergyOutputInterface(BasicGenerator):
    store_rf_max = 160000
    extra_block_names = REG_BLOCK_IDS

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BasicGenerator.__init__(self, dim, x, y, z, block_entity_data)
        self.machine_ref = None # type: ref[BasicGenerator] | None

    def getMachineRef(self):
        # type: () -> BasicGenerator | None
        if self.machine_ref is None:
            return None
        return self.machine_ref()

    def SetMachineRef(self, machine):
        # type: (BasicGenerator) -> None
        self.machine_ref = ref(machine)

    def OutputPower(self, rf):
        # type: (int) -> bool
        return self.GeneratePower(rf)

    def OnTryActivate(self):
        m = self.getMachineRef()
        if m is not None:
            m.OnTryActivate()
