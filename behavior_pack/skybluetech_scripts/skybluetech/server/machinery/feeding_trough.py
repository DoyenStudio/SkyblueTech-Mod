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
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags, id_enum
from .basic import (
    BaseMachine,
    ItemContainer,
    RegisterMachine,
)

ALLOWED_FOODS = frozenset([
    "minecraft:carrot",
    "minecraft:beetroot",
    "minecraft:wheat"
])


@RegisterMachine
class FeedingTrough(BaseMachine, ItemContainer):
    block_name = id_enum.Machinery.FEEDING_TROUGH
    is_non_energy_machine = True
    input_slots = (0,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    def IsValidInput(self, slot, item):
        return slot == 0 and item.id in ALLOWED_FOODS


