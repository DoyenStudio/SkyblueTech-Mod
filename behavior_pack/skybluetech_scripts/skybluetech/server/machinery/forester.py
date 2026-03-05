# coding=utf-8
#
from collections import deque
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName, SetBlock
from skybluetech_scripts.tooldelta.api.server.entity import (
    GetEntitiesBySelector,
    GetDroppedItem,
    DestroyEntity,
    SpawnDroppedItem,
)
from ...common.define.id_enum.machinery import FORESTER as MACHINE_ID
from ...common.machinery_def.forester import getSaplingId, isLog, isLeave
from ...common.ui_sync.machinery.forester import ForesterUISync
from .basic import (
    ItemContainer,
    GUIControl,
    SPControl,
    RegisterMachine,
)

DX = 2
DY = 15
DZ = 2
Y_OFFSET = 2

ALL_NEIGHBOUR_BLOCKS_ENUM = [
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
]


@RegisterMachine
class Forester(GUIControl, ItemContainer, SPControl):
    block_name = MACHINE_ID
    store_rf_max = 16000
    running_power = 80
    origin_process_ticks = 20 * 5
    input_slots = ()
    output_slots = tuple(range(24))

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        SPControl.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ForesterUISync.NewServer(self).Activate()
        self.OnSync()

    def OnTicking(self):
        # 1t 内如果处理多次任务会导致卡顿
        # 直接忽略 1t 内任务的多次处理
        if self.ProcessOnce():
            if self.runOnce():
                self.OnSync()

    def runOnce(self):
        ok = self.collectTree()
        if not ok:
            return False
        item_uqids = GetEntitiesBySelector(
            "@e[type=item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]"
            % (self.x - DX, self.y + Y_OFFSET, self.z - DZ, DX * 2 + 1, DY, DZ * 2 + 1)
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

    def collectTree(self):
        main_log_block, logs, leaves = foresterBFS(
            self.dim, self.x, self.y + Y_OFFSET, self.z, DX, DY, DZ
        )
        sapling_id = getSaplingId(main_log_block)
        if len(logs) + len(leaves) < 10:
            return False
        for x, y, z in logs:
            if not self.PowerEnough():
                return True
            self.ReducePower()
            SetBlock(self.dim, (x, y, z), "minecraft:air", old_block_handing=1)
            if y == self.y + Y_OFFSET:
                SetBlock(self.dim, (x, y, z), sapling_id)
        for x, y, z in leaves:
            SetBlock(self.dim, (x, y, z), "minecraft:air", old_block_handing=1)
        return True

    def canOutput(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and not output_slot_item.StackFull()
        )

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProcessProgress()
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return True

    def OnUnload(self):
        SPControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def OnTryActivate(self):
        self.ResetDeactiveFlags()


def foresterBFS(dim, _x, _y, _z, rx, ry, rz):
    # type: (int, int, int, int, int, int, int) -> tuple[str, set[tuple[int, int, int]], set[tuple[int, int, int]]]
    walked = set()  # type: set[tuple[int, int, int]]
    found_logs = set()  # type: set[tuple[int, int, int]]
    found_leaves = set()  # type: set[tuple[int, int, int]]
    remainings = deque(
        (_x + i, _y + 1, _z + j) for i in range(-rx, rx + 1) for j in range(-rz, rz + 1)
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
            block_id = GetBlockName(dim, next_pos)
            if block_id is None:
                continue
            elif isLog(block_id):
                found_logs.add(next_pos)
                if main_log_block == "":
                    main_log_block = block_id
            elif isLeave(block_id):
                found_leaves.add(next_pos)
            else:
                continue
            remainings.append(next_pos)
    return main_log_block, found_logs, found_leaves
