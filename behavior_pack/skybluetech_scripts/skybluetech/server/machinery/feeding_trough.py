# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockCardinalFacing,
    GetBlockNameAndAux,
    GetBlockStatesFromAuxValue,
    SetBlock,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events import (
    BlockNeighborChangedServerEvent,
    ServerEntityTryPlaceBlockEvent,
)
from ...common.define import flags, id_enum
from .basic import (
    BaseMachine,
    ItemContainer,
)
from .core import RegisterMachine

ALLOWED_FOODS = frozenset([
    "minecraft:carrot",
    "minecraft:beetroot",
    "minecraft:wheat"
])


@RegisterMachine
class FeedingTrough(ItemContainer):
    block_name = id_enum.Machinery.FEEDING_TROUGH
    is_non_energy_machine = True
    item_input_slots = (0,)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FeedingTrough, self).__init__(dim, x, y, z, block_entity_data)

    def IsValidInput(self, slot, item):
        return slot == 0 and item.id in ALLOWED_FOODS
