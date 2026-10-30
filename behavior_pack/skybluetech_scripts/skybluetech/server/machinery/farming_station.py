# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer

from skybluetech_scripts.tooldelta.define.item import Item

from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.farming_station import (
    COMMON_CROP_MAX_GROWTH,
    FRUITLESS_CROPS,
    STORE_RF_MAX,
    isArrisCrop,
    isArrisCropRiped,
    isBlockCrop,
    isCommonCrop,
)
from .basic import GUIControl, UpgradeControl, BaseSpeedControl
from .core import RegisterMachine

DXZ = 2
DXZ_EXPANDED = 8
DZ_EXPANDED = 8
Y_OFFSET = 2


@RegisterMachine
class FarmingStation(UpgradeControl, GUIControl):
    block_name = Machinery.FARMING_STATION
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    running_power = 30
    origin_process_ticks = 20 * 5
    item_input_slots = ()
    item_output_slots = tuple(range(24))
    upgrade_slot_start = 24
    upgrade_slots = 4
    allow_upgraders = frozenset(
        [Upgraders.BASIC_ENERGY_UPGRADER, Upgraders.GENERIC_EXPANSION_UPGRADER]
    )

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FarmingStation, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnTicking(self._farming_station_on_ticking)

    def _farming_station_on_ticking(self):
        # 1t 内如果处理多次任务会导致卡顿
        # 直接忽略 1t 内任务的多次处理
        if BaseSpeedControl.ProcessOnce(self):
            self.run_once()

    def run_once(self):
        ok = self.collect_crops()
        if not ok:
            return False
        item_uqids = CF.CreateEntityComponent("").GetEntitiesBySelector(
            "@e[type=item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]"
            % (
                self.x - self._get_dxz(),
                self.y + Y_OFFSET,
                self.z - self._get_dxz(),
                self._get_dxz() * 2 + 1,
                1,
                self._get_dxz() * 2 + 1,
            )
        )
        items = []
        for item_uqid in item_uqids:
            raw_item = CF.CreateItem(LEVEL_ID).GetDroppedItem(item_uqid, True)
            items.append(Item.from_dict(raw_item) if raw_item is not None else None)
        for item_uqid in item_uqids:
            GetServer().DestroyEntity(item_uqid)
        for item in items:
            if item is None:
                continue
            item_rest = self.OutputItem(item)
            if item_rest is not None:
                GetServer().CreateEngineItemEntity(
                    item_rest.marshal(),
                    self.dim,
                    (self.x, self.y - 1, self.z),
                )
        return True

    def collect_crops(self):
        dim = self.dim
        _x = self.x
        _y = self.y + Y_OFFSET
        _z = self.z
        collected = False
        for x in range(_x - self._get_dxz(), _x + self._get_dxz() + 1):
            for z in range(_z - self._get_dxz(), _z + self._get_dxz() + 1):
                reduce_power = False
                bname = (
                    CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                        (x, _y, z),
                        dim,
                    )
                    or {}
                ).get("name")
                if bname is None:
                    continue
                bstates = CF.CreateBlockState(LEVEL_ID).GetBlockStates((x, _y, z), dim)
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

    def _get_dxz(self):
        # type: () -> int
        if self.HasUpgrader(Upgraders.GENERIC_EXPANSION_UPGRADER):
            return DXZ_EXPANDED
        return DXZ


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
    CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
        xyz,
        {"name": "minecraft:air", "aux": 0},
        1,
        dimensionId=dim,
    )


def _breakAndResetBlock(dim, xyz, block_name):
    # type: (int, tuple[int, int, int], str) -> None
    CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
        xyz,
        {"name": block_name, "aux": 0},
        1,
        dimensionId=dim,
    )
