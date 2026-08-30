# coding=utf-8
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    GetBlockStates,
    SetBlock,
)
from skybluetech_scripts.tooldelta.api.server.entity import (
    DestroyEntity,
    GetDroppedItem,
    GetEntitiesBySelector,
    SpawnDroppedItem,
)
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum.machinery import Machinery
from ...common.machinery_def.farming_station import (
    COMMON_CROP_MAX_GROWTH,
    FRUITLESS_CROPS,
    STORE_RF_MAX,
    isArrisCrop,
    isArrisCropRiped,
    isBlockCrop,
    isCommonCrop,
)
from .basic import GUIControl, ItemContainer, RegisterMachine, SPControl

DX = 2
DZ = 2
Y_OFFSET = 2


@RegisterMachine
class FarmingStation(GUIControl, ItemContainer, SPControl):
    block_name = Machinery.FARMING_STATION
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    running_power = 30
    origin_process_ticks = 20 * 5
    input_slots = ()
    output_slots = tuple(range(24))

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    def OnTicking(self):
        # 1t 内如果处理多次任务会导致卡顿
        # 直接忽略 1t 内任务的多次处理
        if self.ProcessOnce():
            self.run_once()

    def run_once(self):
        ok = self.collect_crops()
        if not ok:
            return False
        item_uqids = GetEntitiesBySelector(
            "@e[type=item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]"
            % (self.x - DX, self.y + Y_OFFSET, self.z - DZ, DX * 2 + 1, 1, DZ * 2 + 1)
        )
        items = [GetDroppedItem(item_uqid, True) for item_uqid in item_uqids]
        for item_uqid in item_uqids:
            DestroyEntity(item_uqid)
        for item in items:
            if item is None:
                continue
            item_rest = self.OutputItem(item)
            if item_rest is not None:
                SpawnDroppedItem(self.dim, (self.x, self.y - 1, self.z), item_rest)
        return True

    def collect_crops(self):
        dim = self.dim
        _x = self.x
        _y = self.y + Y_OFFSET
        _z = self.z
        collected = False
        for x in range(_x - DX, _x + DX + 1):
            for z in range(_z - DZ, _z + DZ + 1):
                reduce_power = False
                bname = GetBlockName(dim, (x, _y, z))
                if bname is None:
                    continue
                bstates = GetBlockStates(dim, (x, _y, z))
                if bstates is None:
                    continue
                if isRipedCrop(bname, bstates):
                    _breakAndResetBlock(dim, (x, _y, z), bname)
                    reduce_power = True
                elif isBlockCrop(bname):
                    _breakBlock(dim, (x, _y, z))
                    reduce_power = True
                if reduce_power:
                    collected = True
                    self.ReducePower()
                    if not self.PowerEnough():
                        return collected
        return collected

    def can_output(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and not output_slot_item.StackFull()
        )

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass


def isRipedCrop(block_name, block_states):
    # type: (str, dict) -> bool
    if block_name in FRUITLESS_CROPS:
        return False
    if isCommonCrop(block_states):
        max_growth = COMMON_CROP_MAX_GROWTH.get(block_name, 7)
        return block_states.get("growth") == max_growth
    elif isArrisCrop(block_name, block_states):
        return isArrisCropRiped(block_name, block_states)
    else:
        return False


def _breakBlock(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    SetBlock(dim, xyz, "minecraft:air", old_block_handing=1)


def _breakAndResetBlock(dim, xyz, block_name):
    # type: (int, tuple[int, int, int], str) -> None
    SetBlock(dim, xyz, block_name, old_block_handing=1)

