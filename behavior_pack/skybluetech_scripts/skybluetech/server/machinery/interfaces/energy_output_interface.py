# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from ..basic import BasicGenerator, RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyOutputInterface(BaseInterface, BasicGenerator):
    store_rf_max = 160000

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BasicGenerator.__init__(self, dim, x, y, z, block_entity_data)
        BaseInterface.__init__(self, dim, x, y, z, block_entity_data)

    def OutputPower(self, rf):
        # type: (int) -> bool
        return self.GeneratePower(rf)

    def OnTryActivate(self):
        m = self.getMachineRef()
        if m is not None:
            m.OnTryActivate()
