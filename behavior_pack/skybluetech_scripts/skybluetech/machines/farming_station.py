# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName, GetBlockStates, SetBlock
from skybluetech_scripts.tooldelta.api.server.entity import (
    GetEntitiesBySelector,
    GetDroppedItem,
    DestroyEntity,
    SpawnDroppedItem,
)
from ..define.machine_config.farming_station import (
    isRipedCrop,
    isBlockCrop,
)
from ..ui_sync.machines.farming_station import FarmingStationUISync
from .basic import AutoSaver, BaseMachine, ItemContainer, GUIControl, SPControl, RegisterMachine

DX = 2
DZ = 2
Y_OFFSET = 2


@RegisterMachine
class FarmingStation(AutoSaver, GUIControl, ItemContainer, SPControl):
    block_name = "skybluetech:farming_station"
    store_rf_max = 16000
    running_power = 30
    origin_process_ticks = 20 * 5
    input_slots = ()
    output_slots = tuple(range(24))

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = FarmingStationUISync.NewServer(self).Activate()
        self.OnSync()

    def OnTicking(self):
        # 1t 内如果处理多次任务会导致卡顿
        # 直接忽略 1t 内任务的多次处理
        if self.ProcessOnce():
            if self.runOnce():
                self.OnSync()

    def runOnce(self):
        ok = self.collectCrops()
        if not ok:
            return False
        item_uqids = GetEntitiesBySelector(
            "@e[type=item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]"
            % (self.x-DX, self.y+Y_OFFSET, self.z-DZ, DX*2+1, 1, DZ*2+1)
        )
        items = [GetDroppedItem(item_uqid, True) for item_uqid in item_uqids]
        for item_uqid in item_uqids:
            DestroyEntity(item_uqid)
        for item in items:
            item_rest = self.OutputItem(item)
            if item_rest is not None:
                SpawnDroppedItem(self.dim, (self.x, self.y - 1, self.z), item_rest)
        return True

    def collectCrops(self):
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
                    breakAndResetBlock(dim, (x, _y, z), bname)
                    reduce_power = True
                elif isBlockCrop(bname):
                    breakBlock(dim, (x, _y, z))
                    reduce_power = True
                if reduce_power:
                    collected = True
                    self.ReducePower()
                    if not self.PowerEnough():
                        return collected
        return collected

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

    def OnTryActivate(self):
        self.ResetDeactiveFlags()

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)


def breakBlock(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    SetBlock(dim, xyz, "minecraft:air", old_block_handing=1)

def breakAndResetBlock(dim, xyz, block_name):
    # type: (int, tuple[int, int, int], str) -> None
    SetBlock(dim, xyz, block_name, old_block_handing=1)
    

