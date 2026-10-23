# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    ItemExists,
)
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from ..basic import MultiFluidContainer, ItemContainer, GUIControl
from ..utils.transmitter_conn import TransmitterConn


TCON = TransmitterConn(fluid_pipe=True)

registered_tanks = {}  # type: dict[str, type[BasicTank]]
FIRST_TANK_LOADED = False


class BasicTank(GUIControl, ItemContainer, MultiFluidContainer):
    is_non_energy_machine = True
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = {0: 0}
    fluid_input_slots = (0,)
    fluid_output_slots = (0,)
    migrate_legacy_fluid_data = True
    item_input_slots = (0,)
    item_output_slots = (1,)

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
        fluid = self.fluids[0]
        item0 = self.GetSlotItem(0)
        item1 = self.GetSlotItem(1)
        if item0 is not None:
            if item0.id == "minecraft:bucket":
                if (
                    item1 is not None
                    or fluid.fluid_id is None
                    or fluid.volume < BUCKET_VOLUME
                ):
                    return
                fluid_id = fluid.fluid_id
                bucket_id = fluid_id + "_bucket"
                if not ItemExists(bucket_id):
                    return
                # TODO: 我们只能假定桶 id 是液体 id + "_bucket"
                fluid.volume -= BUCKET_VOLUME
                self.SetSlotItem(1, Item(bucket_id))
                item0.count -= 1
                self.SetSlotItem(0, item0)
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
                    or not ItemExists(fluid_id)
                ):
                    return
                if fluid.fluid_id is None:
                    fluid.fluid_id = fluid_id
                fluid.volume += BUCKET_VOLUME
                item0.count -= 1
                self.SetSlotItem(0, item0 if item0.count > 0 else None)
                if item1 is None:
                    item1 = Item("minecraft:bucket", count=0)
                    # TODO: 如果其他模组的捅倒空不是 minecraft:bucket 则出问题
                item1.count += 1
                self.SetSlotItem(1, item1)
                self._on_added_fluid(0, fluid_id, BUCKET_VOLUME, True)


def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class
