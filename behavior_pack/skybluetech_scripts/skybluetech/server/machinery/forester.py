# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from collections import deque


from skybluetech_scripts.tooldelta.define.item import Item

from .basic.item_container import ItemContainer
from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.forester import STORE_RF_MAX, ForesterUtils
from .basic import (
    BaseSpeedControl,
    GUIControl,
    UpgradeControl,
)
from .core import RegisterMachine

DX = 8
DY = 32
DZ = 8
Y_OFFSET = 2
DX_EXPANDED = 20
DY_EXPANDED = 128
SEED_RADIUS = 2

ALL_NEIGHBOUR_BLOCKS_ENUM = [
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
]


@RegisterMachine
class Forester(UpgradeControl, GUIControl):
    block_name = Machinery.FORESTER
    store_rf_max = STORE_RF_MAX
    running_power = 80
    origin_process_ticks = 20 * 5
    item_input_slots = ()
    item_output_slots = tuple(range(24))
    upgrade_slot_start = 24
    upgrade_slots = 4
    allow_upgraders = frozenset({
        Upgraders.BASIC_ENERGY_UPGRADER,
        Upgraders.GENERIC_AUTO_EJECTION, 
        Upgraders.GENERIC_EXPANSION_UPGRADER,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Forester, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnTicking(self._forester_on_ticking)

    def _forester_on_ticking(self):
        # 1t 内如果处理多次任务会导致卡顿
        # 直接忽略 1t 内任务的多次处理
        if BaseSpeedControl.ProcessOnce(self):
            # 每轮都刷新能量不足标志 (同种植站): 范围内没有树时 collect_tree 不检查能量,
            # 没接电源时也没有 AddPower 来更新它
            self.PowerEnough()
            self.run_once()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._forester_is_valid_input(slot, item),
        )
        return all(results)

    def _forester_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return True

    def _get_dx(self):
        # type: () -> int
        if self.HasUpgrader(Upgraders.GENERIC_EXPANSION_UPGRADER):
            return DX_EXPANDED
        return DX

    def _get_dy(self):
        # type: () -> int
        if self.HasUpgrader(Upgraders.GENERIC_EXPANSION_UPGRADER):
            return DY_EXPANDED
        return DY


    def run_once(self):
        ok = self.collect_tree()
        if not ok:
            return False
        dx = self._get_dx()
        item_uqids = CF.CreateEntityComponent("").GetEntitiesBySelector("@e[type=item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]"
            % (
                self.x - dx,
                self.y + Y_OFFSET,
                self.z - dx,
                dx * 2 + 1,
                self._get_dy(),
                dx * 2 + 1,
            ))
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

    def collect_tree(self):
        main_log_block, logs, leaves = forester_bfs(
            self.dim,
            self.x,
            self.y + Y_OFFSET,
            self.z,
            self._get_dx(),
            self._get_dy(),
            self._get_dx(),
            )
        sapling_id = ForesterUtils.GetSaplingId(main_log_block)
        if len(logs) + len(leaves) < 10:
            return False
        for x, y, z in logs:
            if not self.PowerEnough():
                return True
            self.ReducePower()
            CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                (x, y, z),
                {"name": "minecraft:air", "aux": 0},
                1,
                dimensionId=self.dim,
            )
            if y == self.y + Y_OFFSET:
                CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                    (x, y, z),
                    {"name": sapling_id, "aux": 0},
                    0,
                    dimensionId=self.dim,
                )
        for x, y, z in leaves:
            CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                (x, y, z),
                {"name": "minecraft:air", "aux": 0},
                1,
                dimensionId=self.dim,
            )
        return True

    def can_output(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and not output_slot_item.StackFull()
        )


def forester_bfs(dim, _x, _y, _z, rx, ry, rz):
    # type: (int, int, int, int, int, int, int) -> tuple[str, set[tuple[int, int, int]], set[tuple[int, int, int]]]
    walked = set()  # type: set[tuple[int, int, int]]
    found_logs = set()  # type: set[tuple[int, int, int]]
    found_leaves = set()  # type: set[tuple[int, int, int]]
    remainings = deque(
        (_x + i, _y + 1, _z + j)
        for i in range(-SEED_RADIUS, SEED_RADIUS + 1)
        for j in range(-SEED_RADIUS, SEED_RADIUS + 1)
    )
    main_log_block = ""
    while len(remainings) > 0:
        x, y, z = remainings.popleft()
        for dx, dy, dz in ALL_NEIGHBOUR_BLOCKS_ENUM:
            new_x = x + dx
            new_y = y + dy
            new_z = z + dz
            if (
                new_x < _x - rx
                or new_x > _x + rx
                or new_y < _y
                or new_y > _y + ry
                or new_z < _z - rz
                or new_z > _z + rz
            ):
                continue
            next_pos = (new_x, new_y, new_z)
            if next_pos in walked:
                continue
            walked.add(next_pos)
            block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(next_pos, dim) or {}).get("name")
            if block_id is None:
                continue
            elif ForesterUtils.IsLog(block_id):
                found_logs.add(next_pos)
                if main_log_block == "":
                    main_log_block = block_id
            elif ForesterUtils.IsLeave(block_id):
                found_leaves.add(next_pos)
            else:
                continue
            remainings.append(next_pos)
    return main_log_block, found_logs, found_leaves
