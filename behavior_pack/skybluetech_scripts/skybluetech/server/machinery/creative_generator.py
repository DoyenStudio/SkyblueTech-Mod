# coding=utf-8

from ...common.define.id_enum import Machinery
from .basic import BaseGenerator
from .core import RegisterMachine


@RegisterMachine
class CreativeGenerator(BaseGenerator):
    block_name = Machinery.CREATIVE_GENERATOR
    store_rf_max = 2147483647
    energy_io_mode = (1, 1, 1, 1, 1, 1)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(CreativeGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self.SetOutputPower(2147483647)
