# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetDroppedItem,
    GetEntitiesInSquareArea,
    GetBlockBasicInfo,
    DestroyEntity,
    SetBlock,
    SpawnDroppedItem,
)
from ...common.define import flags
from ...common.define.id_enum.machinery import MINI_MINER as MACHINE_ID
from ...common.machinery_def.mini_miner import (
    VOLUME_COST_ONCE,
    USE_FLUID,
    BLOCK_CAN_MINE,
)
from ...common.ui_sync.machinery.mini_miner import MiniMinerUISync
from .basic import FluidContainer, GUIControl, UpgradeControl, RegisterMachine

# TODO: 会使领地模组失效
K_MINING_FINISHED = "mining_finished"
K_LAST_SCANNED_Y = "last_scanned_y"


@RegisterMachine
class MiniMiner(FluidContainer, GUIControl, UpgradeControl):
    block_name = MACHINE_ID
    max_fluid_volume = 2000
    fluid_io_fix_mode = 0
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    output_slots = (0, 1, 2, 3, 4, 5, 6, 7)
    running_power = 200
    upgrade_slot_start = 8
    origin_process_ticks = 20

    def __init__(self, dim, x, y, z, block_entity_data):
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MiniMinerUISync.NewServer(self).Activate()
        self.size_x = 15
        self.size_y = 64
        self.size_z = 15
        self._cached_mining_finished = None
        self._fast_skiped = False
        self.init_mining_area()
        if not self.mining_finished:
            self.init_mine_pos_iterator()
        else:
            self.mine_pos_iterator = None
        self.init_flags()

    def OnSlotUpdate(self, slot):
        # type: (int) -> None
        UpgradeControl.OnSlotUpdate(self, slot)

    def OnFluidSlotUpdate(self):
        if self.fluid_id != USE_FLUID or self.fluid_volume < VOLUME_COST_ONCE:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            # code: UnsetDeactiveFlag first use HasDeactiveFlag
        elif self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)

    def OnTicking(self):
        FluidContainer.OnTicking(self)
        if not self.mining_finished:
            if not self.fast_skip():
                return
            if self.IsActive():
                if self.ProcessOnce():
                    self.run_once()
                    self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.fluid_id = self.fluid_id
        self.sync.fluid_volume = self.fluid_volume
        self.sync.max_volume = self.max_fluid_volume
        self.sync.MarkedAsChanged()

    def OnUnload(self):
        GUIControl.OnUnload(self)
        UpgradeControl.OnUnload(self)

    def OnTryActivate(self):
        FluidContainer.OnTryActivate(self)

    def OnDeactiveFlagsChanged(self):
        self.update_gui_states()
    
    def init_flags(self):
        if self.fluid_id != USE_FLUID or self.fluid_volume < VOLUME_COST_ONCE:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        if self.OutputItem(Item("minecraft:air")):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def init_mining_area(self):
        x_offset = -self.size_x // 2
        y_offset = -self.size_y
        z_offset = -self.size_z // 2
        self.mining_area_volume = self.size_x * self.size_y * self.size_z
        self.mining_min_x = self.x + x_offset
        self.mining_max_x = self.x + x_offset + self.size_x
        self.mining_min_y = max(-63, self.y + y_offset)
        self.mining_max_y = self.y + y_offset + self.size_y
        self.mining_min_z = self.z + z_offset
        self.mining_max_z = self.z + z_offset + self.size_z

    def fast_skip(self):
        if self._fast_skiped:
            print "fast skip 1"
            return True
        elif self.mine_pos_iterator is None:
            print "fast skip 2"
            self._fast_skiped = True
            return True
        try:
            x, y, z = next(self.mine_pos_iterator)
        except StopIteration:
            self.last_scanned_y = self.y
            self._fast_skiped = True
            self.mining_finished = True
            return True
        if self.last_scanned_y is None:
            self.last_scanned_y = y
        self.last_scanned_y = max(self.last_scanned_y, y)
        block_id = GetBlockName(self.dim, (x, y, z))
        if block_id is None or not self.can_mine_block(block_id):
            return False
        else:
            print "fast skip 3", block_id
            self._fast_skiped = True
            return True

    def update_gui_states(self):
        myflags = self.deactive_flags
        if myflags & flags.DEACTIVE_FLAG_OUTPUT_FULL:
            self.sync.work_mode = MiniMinerUISync.WorkMode.OUTPUT_FULL
        elif myflags & flags.DEACTIVE_FLAG_NO_INPUT:
            self.sync.work_mode = MiniMinerUISync.WorkMode.FLUID_LACK
        elif myflags & flags.DEACTIVE_FLAG_POWER_LACK:
            self.sync.work_mode = MiniMinerUISync.WorkMode.POWER_LACK
        elif myflags != 0:
            print "fast skip 4", myflags
            self.sync.work_mode = MiniMinerUISync.WorkMode.OTHER
        else:
            self.sync.work_mode = MiniMinerUISync.WorkMode.WORKING
        self.OnSync()

    def init_mine_pos_iterator(self):
        if self.last_scanned_y is not None:
            start_y = self.last_scanned_y
        else:
            start_y = self.mining_min_y
        self.mine_pos_iterator = (
            (x, y, z)
            for y in range(start_y, self.mining_max_y + 1)
            for x in range(self.mining_min_x, self.mining_max_x + 1)
            for z in range(self.mining_min_z, self.mining_max_z + 1)
        )

    def run_once(self):
        if self.mine_pos_iterator is None:
            return
        try:
            x, y, z = next(self.mine_pos_iterator)
            self.sync.digging_pos = (x, y, z)
            self.last_scanned_y = y
        except StopIteration:
            self.mine_pos_iterator = None
            self.mining_finished = True
            self.sync.work_mode = self.sync.WorkMode.FINISHED
            self.sync.digging_pos = (0, 0, 0)
            return
        self.fluid_volume -= VOLUME_COST_ONCE
        if self.fluid_volume <= 0:
            self.fluid_id = None
        if self.fluid_volume < VOLUME_COST_ONCE:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        block_id = GetBlockName(self.dim, (x, y, z))
        if block_id is None or not self.can_mine_block(block_id):
            self._fast_skiped = False
            return
        items = self.mine_and_collect(x, y, z)
        for item in items:
            rest = self.OutputItem(item)
            if rest is not None:
                SpawnDroppedItem(self.dim, (self.x, self.y + 1, self.z), rest)
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
        self.SelfRequireFluid()

    def mine_and_collect(self, mx, my, mz):
        # type: (int, int, int) -> list[Item]
        res = SetBlock(
            self.dim,
            (mx, my, mz),
            "minecraft:air",
            old_block_handing=1,
        )
        if res is None:
            return []
        entity_ids = GetEntitiesInSquareArea(
            None, (mx, my, mz), (mx + 1, my + 1, mz + 1), self.dim
        )
        items = []  # type: list[Item]
        for entity_id in entity_ids:
            res = GetDroppedItem(entity_id, get_user_data=True)
            if res is None:
                continue
            items.append(res)
            DestroyEntity(entity_id)
        return items

    def can_mine_block(self, block_id):
        # type: (str) -> bool
        if block_id in BLOCK_CAN_MINE:
            return True
        elif not block_id.endswith("_ore"):
            return False
        destroy_time = GetBlockBasicInfo(block_id).destroyTime
        return destroy_time > 0 and destroy_time < 40

    @property
    def mining_finished(self):
        # type: () -> bool
        if self._cached_mining_finished is None:
            self._cached_mining_finished = self.bdata[K_MINING_FINISHED] or False
        return self._cached_mining_finished

    @mining_finished.setter
    def mining_finished(self, value):
        # type: (bool) -> None
        self.bdata[K_MINING_FINISHED] = self._cached_mining_finished = value

    @property
    def last_scanned_y(self):
        # type: () -> int | None
        return self.bdata[K_LAST_SCANNED_Y]

    @last_scanned_y.setter
    def last_scanned_y(self, value):
        # type: (int) -> None
        self.bdata[K_LAST_SCANNED_Y] = value
