# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import CREATIVE_GENERATOR as MACHINE_ID
from .basic import BaseGenerator, RegisterMachine


@RegisterMachine
class CreativeGenerator(BaseGenerator):
    block_name = MACHINE_ID
    store_rf_max = 2147483647
    energy_io_mode = (1, 1, 1, 1, 1, 1)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.SetOutputPower(2147483647)
