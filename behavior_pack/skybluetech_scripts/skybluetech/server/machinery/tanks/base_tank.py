# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    ItemExists,
)
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from ..basic import BaseMachine, FluidContainer, ItemContainer, GUIControl
from ..utils.transmitter_conn import TransmitterConn


TCON = TransmitterConn(pipe=True)

INFINITY = float("inf")
registered_tanks = {}  # type: dict[str, type[BasicTank]]
FIRST_TANK_LOADED = False


class BasicTank(BaseMachine, FluidContainer, ItemContainer, GUIControl):
    is_non_energy_machine = True
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_io_fix_mode = 0
    max_fluid_volume = 0
    input_slots = (0,)
    output_slots = (1,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        TCON.block_placed(self)

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        item0 = self.GetSlotItem(0)
        item1 = self.GetSlotItem(1)
        if item0 is not None:
            if item0.id == "minecraft:bucket":
                if (
                    item1 is not None
                    or self.fluid_id is None
                    or self.fluid_volume < BUCKET_VOLUME
                ):
                    return
                fluid_id = self.fluid_id
                bucket_id = fluid_id + "_bucket"
                if not ItemExists(bucket_id):
                    return
                # TODO: 我们只能假定桶 id 是液体 id + "_bucket"
                self.fluid_volume -= BUCKET_VOLUME
                if self.fluid_volume <= 0:
                    self.fluid_id = None
                self.SetSlotItem(1, Item(bucket_id))
                item0.count -= 1
                self.SetSlotItem(0, item0)
                self._on_reduced_fluid(fluid_id, BUCKET_VOLUME)
            elif item0.id.endswith("_bucket"):
                if item1 is not None and (
                    item1.id != "minecraft:bucket" or item1.StackFull()
                ):
                    return
                fluid_id = item0.id[: -len("_bucket")]
                if (
                    (self.fluid_id is not None and self.fluid_id != fluid_id)
                    or self.fluid_volume + BUCKET_VOLUME > self.max_fluid_volume
                    or not ItemExists(fluid_id)
                ):
                    return
                if self.fluid_id is None:
                    self.fluid_id = fluid_id
                self.fluid_volume += BUCKET_VOLUME
                self.SetSlotItem(0, None)
                if item1 is None:
                    item1 = Item("minecraft:bucket", count=0)
                    # TODO: 如果其他模组的捅倒空不是 minecraft:bucket 则出问题
                item1.count += 1
                self.SetSlotItem(1, item1)
                self._on_added_fluid(fluid_id, BUCKET_VOLUME)


def RegisterTank(tank_class):
    # type: (type[BasicTank]) -> type[BasicTank]
    registered_tanks[tank_class.block_name] = tank_class
    return tank_class
