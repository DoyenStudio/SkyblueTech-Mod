# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockNameAndAux,
    GetBlockBasicInfo,
    SetBlock,
    GetBlockFacingDir,
)
from skybluetech_scripts.tooldelta.api.server.entity import (
    GetEntitiesBySelector,
    GetDroppedItem,
    DestroyEntity,
    SpawnDroppedItem,
)
from ...common.define import flags
from ...common.events.machinery.digger import (
    DiggerWorkModeUpdatedEvent,
    DiggerUpdateCrack,
)
from ...common.define.id_enum.machinery import DIGGER as MACHINE_ID
from ...common.machinery.utils.block_sync import BlockSync
from ...common.ui_sync.machinery.digger import DiggerUISync
from .basic import (
    GUIControl,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)

TICKS_PER_SECOND = 20
block_sync = BlockSync(MACHINE_ID)


@RegisterMachine
class Digger(GUIControl, UpgradeControl, WorkRenderer):
    block_name = MACHINE_ID
    input_slots = ()
    output_slots = (0,)
    store_rf_max = 8800
    running_power = 40
    upgrade_slot_start = 1
    upgrade_slots = 4
    allow_upgrader_tags = {
        "skybluetech:upgraders/speed",
        "skybluetech:upgraders/energy",
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.dx, self.dy, self.dz = GetOppositeDirFromFacing(
            GetBlockFacingDir(self.dim, (x, y, z))
        )
        self.front_block, self.front_block_aux = GetBlockNameAndAux(
            self.dim, (x + self.dx, y + self.dy, z + self.dz)
        )  # block is None?
        self.sync = DiggerUISync.NewServer(self).Activate()
        self.OnSync()
        self.prev_crack_stage = 0
        # NOTE: 我们假设方块之后的朝向直到方块被销毁前都不会变化

    def OnPlaced(self, _):
        self.startNext()

    def OnTicking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.runOnce()
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            else:
                crack_stage = int(self.GetProcessProgress() * 10)
                if crack_stage != self.prev_crack_stage:
                    self.prev_crack_stage = crack_stage
                    self.updateCrackToClients()
                break
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProcessProgress()
        self.sync.block_id = self.front_block
        self.sync.block_aux = self.front_block_aux
        self.sync.MarkedAsChanged()

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if (
            event.neighborPosX - self.x == self.dx
            and event.neighborPosY - self.y == self.dy
            and event.neighborPosZ - self.z == self.dz
        ):
            self.startNext((event.toBlockName, event.toAuxValue))
            self.OnSync()

    def OnUnload(self):
        # type: () -> None
        UpgradeControl.OnUnload(self)
        GUIControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        UpgradeControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def OnWorkStatusUpdated(self):
        DiggerWorkModeUpdatedEvent(self.x, self.y, self.z, self.IsActive()).sendMulti(
            block_sync.get_players((self.dim, self.x, self.y, self.z))
        )

    def startNext(self, new_block=None):
        # type: (tuple[str, int] | None) -> None
        block_name, block_aux = new_block or GetBlockNameAndAux(
            self.dim, (self.x + self.dx, self.y + self.dy, self.z + self.dz)
        )
        self.front_block = block_name
        self.front_block_aux = block_aux
        if block_name is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        basic = GetBlockBasicInfo(block_name)
        if basic.destroyTime <= 0.0 or basic.destroyTime == 100.0:
            # 水 ~ = 100
            self.front_block = "minecraft:air"
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        # 会不会因为 0t 破坏而出现问题...
        self.SetProcessTicks(int(basic.destroyTime * TICKS_PER_SECOND))
        self.ResetProgress()

    def runOnce(self):
        SetBlock(
            self.dim,
            (self.x + self.dx, self.y + self.dy, self.z + self.dz),
            "minecraft:air",
            old_block_handing=1,
        )
        self.collect()

    def collect(self):
        item_uqids = GetEntitiesBySelector(
            "@e[type=item,x=%d,y=%d,z=%d,r=1.5]"
            % (self.x + self.dx, self.y + self.dy, self.z + self.dz)
        )
        items = [GetDroppedItem(item_uqid, True) for item_uqid in item_uqids]
        for item_uqid in item_uqids:
            DestroyEntity(item_uqid)
        for item in items:
            item_rest = self.OutputItem(item)
            if item_rest is not None:
                SpawnDroppedItem(
                    self.dim,
                    (self.x - self.dx, self.y - self.dy, self.z - self.dz),
                    item_rest,
                )

    def updateCrackToClients(self):
        DiggerUpdateCrack(
            self.dim,
            self.x + self.dx,
            self.y + self.dy,
            self.z + self.dz,
            self.prev_crack_stage,
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))


def GetOppositeDirFromFacing(facing):
    # type: (str) -> tuple[int, int, int]
    return {
        "north": (0, 0, 1),
        "south": (0, 0, -1),
        "east": (-1, 0, 0),
        "west": (1, 0, 0),
        "up": (0, -1, 0),
        "down": (0, 1, 0),
    }[facing]
