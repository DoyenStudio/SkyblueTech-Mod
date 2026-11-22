# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item

from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from ..basic import MultiFluidContainer, GUIControl
from ..basic.upgrade_control import ItemUpgradeControl
from ..utils.transmitter_conn import TransmitterConn


TCON = TransmitterConn(fluid_pipe=True)

registered_tanks = {}  # type: dict[str, type[BasicTank]]
FIRST_TANK_LOADED = False


class BasicTank(GUIControl, ItemUpgradeControl, MultiFluidContainer):
    is_non_energy_machine = True
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = {0: 0}
    fluid_input_slots = (0,)
    fluid_output_slots = (0,)
    migrate_legacy_fluid_data = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BasicTank, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnPlaced(self._basic_tank_on_placed)
        self.handler.SubscribeOnNeighborChanged(self._basic_tank_on_neighbor_changed)
        self.handler.SubscribeOnSlotUpdate(self._basic_tank_on_slot_update)

    def _basic_tank_on_placed(self, _):
        TCON.block_placed(self)

    def _basic_tank_on_neighbor_changed(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)

    def _basic_tank_on_slot_update(self, slot_pos):
        # type: (int) -> None
        if slot_pos not in (0, 1):
            return
        fluid = self.fluids[0]
        item0 = self.GetSlotItem(0)
        if item0 is None:
            return
        item1 = self.GetSlotItem(1)
        if item0.id == "minecraft:bucket":
            fluid_id = fluid.fluid_id
            if item1 is not None or fluid_id is None or fluid.volume < BUCKET_VOLUME:
                return
            # 现有桶命名约定为液体 id + "_bucket"。
            bucket_id = fluid_id + "_bucket"
            if not CF.CreateGame(LEVEL_ID).LookupItemByName(bucket_id):
                return
            if not self._store_bucket_result(item0, item1, Item(bucket_id)):
                return
            fluid.volume -= BUCKET_VOLUME
            self._on_reduced_fluid(0, fluid_id, BUCKET_VOLUME, True)
        elif item0.id.endswith("_bucket"):
            if item1 is not None and (
                item1.id != "minecraft:bucket" or item1.StackFull()
            ):
                return
            fluid_id = item0.id[: -len("_bucket")]
            if (
                fluid.isFull()
                or (fluid.fluid_id is not None and fluid.fluid_id != fluid_id)
                or fluid.volume + BUCKET_VOLUME > fluid.max_volume
                or not CF.CreateGame(LEVEL_ID).LookupItemByName(fluid_id)
            ):
                return
            empty_bucket = Item("minecraft:bucket", count=0) if item1 is None else item1.copy()
            empty_bucket.count += 1
            if not self._store_bucket_result(item0, item1, empty_bucket):
                return
            if fluid.fluid_id is None:
                fluid.fluid_id = fluid_id
            fluid.volume += BUCKET_VOLUME
            self._on_added_fluid(0, fluid_id, BUCKET_VOLUME, True)
        else:
            return
        self.FlushOutputSlots(self.item_output_slots)

    def _store_bucket_result(self, input_item, previous_output, bucket):
        # type: (Item, Item | None, Item) -> bool
        if not self.SetSlotItem(1, bucket):
            return False
        input_item.count -= 1
        if self.SetSlotItem(0, input_item if input_item.count > 0 else None):
            return True
        self.SetSlotItem(1, previous_output)
        return False


def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class
