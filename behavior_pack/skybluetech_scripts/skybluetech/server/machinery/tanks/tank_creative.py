# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import ItemExists
from skybluetech_scripts.skybluetech.common.define.id_enum import Tank
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from ..basic import RegisterMachine
from .base_tank import BasicTank, FluidContainer, RegisterTank

INFINITY = float("inf")


@RegisterMachine
@RegisterTank
class CreativeTank(BasicTank):
    block_name = Tank.CREATIVE
    max_fluid_volume = TANK_MAX_VOLUMES[Tank.CREATIVE]

    def __init__(self, dim, x, y, z, block_entity_data):
        BasicTank.__init__(self, dim, x, y, z, block_entity_data)
        # 无限体积无法可靠地持久化到方块实体数据, 重载时按存有流体的事实重置为
        # INFINITY, 即使存档中的数值被损坏也能自愈。
        if self.fluid_id is not None:
            self.fluid_volume = INFINITY

    def AddFluid(self, fluid_id, fluid_volume, depth=0):
        # type: (str, float, int) -> tuple[bool, float]
        if self.fluid_id is None:
            return True, 0
        else:
            return False, fluid_volume

    def on_player_interact_with_bucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        res = FluidContainer.on_player_interact_with_bucket(self, player_id, test)
        if self.fluid_id is not None:
            self.fluid_volume = INFINITY
        self.CallSync()
        return res

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        item0 = self.GetSlotItem(0)
        item1 = self.GetSlotItem(1)
        if item0 is not None:
            if item0.id == "minecraft:bucket":
                if item1 is not None or self.fluid_id is None:
                    return
                fluid_id = self.fluid_id
                bucket_id = fluid_id + "_bucket"
                if not ItemExists(bucket_id):
                    return
                # TODO: 我们只能假定桶 id 是液体 id + "_bucket"
                self.SetSlotItem(1, Item(bucket_id))
                item0.count -= 1
                self.SetSlotItem(0, item0)
                self.CallSync()
            elif item0.id.endswith("_bucket"):
                if item1 is not None and (
                    item1.id != "minecraft:bucket" or item1.StackFull()
                ):
                    return
                fluid_id = item0.id[: -len("_bucket")]
                if self.fluid_id is not None or not ItemExists(fluid_id):
                    return
                self.SetSlotItem(0, None)
                if item1 is None:
                    item1 = Item("minecraft:bucket", count=0)
                    # TODO: 如果其他模组的捅倒空不是 minecraft:bucket 则出问题
                item1.count += 1
                self.SetSlotItem(1, item1)
                self.CallSync()
