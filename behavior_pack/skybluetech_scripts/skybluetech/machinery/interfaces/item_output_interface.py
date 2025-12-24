# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..basic import BaseMachine, ItemContainer, RegisterMachine

# LOADED_INTERFACES
#

REG_BLOCK_IDS = (
)


@RegisterMachine
class ItemOutputInterface(BaseMachine, ItemContainer):
    extra_block_names = REG_BLOCK_IDS
    is_non_energy_machine = True
    input_slots = ()
    output_slots = (0, 1, 2, 3, 4)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
