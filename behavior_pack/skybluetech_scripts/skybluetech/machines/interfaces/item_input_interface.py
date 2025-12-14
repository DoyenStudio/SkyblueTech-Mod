# coding=utf-8
#
from weakref import ref
from mod.server.blockEntityData import BlockEntityData
from ..basic import BaseMachine, ItemContainer, RegisterMachine

from ...define.machine_config import (
    fermenter
)

REG_BLOCK_IDS = (
    fermenter.IO_ITEM,
)


@RegisterMachine
class ItemInputInterface(BaseMachine, ItemContainer):
    extra_block_names = REG_BLOCK_IDS
    is_non_energy_machine = True
    input_slots = (0, 1, 2, 3, 4)
    output_slots = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
