# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    UiInitFinishedEvent,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockNameAndAux,
    GetBlockBasicInfo,
    SetBlock,
    GetBlockFacingDir,
)
from skybluetech_scripts.tooldelta.api.client.block import (
    GetBlockNameAndAux as CGetBlockNameAndAux,
    GetBlockName,
    SetBlockEntityMolangValue,
    SetCrackFrame,
)
from skybluetech_scripts.tooldelta.api.server.entity import (
    GetEntitiesBySelector,
    GetDroppedItem,
    DestroyEntity,
    SpawnDroppedItem,
)
from skybluetech_scripts.tooldelta.api.server.player import GetPlayersInDim
from skybluetech_scripts.tooldelta.events.notify import NotifyToClients
from ..define import flags
from ..define.events.digger import DiggerWorkModeUpdatedEvent, DiggerUpdateCrack
from ..utils.facing import GetOppositeDirFromFacing
from ..ui_sync.machines.digger import DiggerUISync
from .basic import (
    AutoSaver,
    GUIControl,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)

TICKS_PER_SECOND = 20


@RegisterMachine
class Digger(AutoSaver, GUIControl, UpgradeControl, WorkRenderer):
    block_name = "skybluetech:digger"
    input_slots = ()
    output_slots = (0,)
    store_rf_max = 8800
    running_power = 40
    upgrade_slot_start = 1
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        self.dx, self.dy, self.dz = GetOppositeDirFromFacing(
            GetBlockFacingDir(self.dim, (x, y, z))
        )
        print(self.dx, self.dy, self.dz)
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
        AutoSaver.OnUnload(self)
        UpgradeControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        UpgradeControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def Dump(self):
        UpgradeControl.Dump(self)

    def OnWorkStatusUpdated(self):
        NotifyToClients(
            GetPlayersInDim(self.dim),
            DiggerWorkModeUpdatedEvent(self.x, self.y, self.z, self.IsActive()),
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
        NotifyToClients(
            GetPlayersInDim(self.dim),
            DiggerUpdateCrack(
                self.dim,
                self.x + self.dx,
                self.y + self.dy,
                self.z + self.dz,
                self.prev_crack_stage,
            ),
        )


@DiggerWorkModeUpdatedEvent.Listen()
def clientOnDiggerWorkModeUpdated(event):
    # type: (DiggerWorkModeUpdatedEvent) -> None
    res = SetBlockEntityMolangValue(
        (event.x, event.y, event.z), "variable.mod_block_is_active", event.active
    )


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName == Digger.block_name:
        _, aux = CGetBlockNameAndAux((event.posX, event.posY, event.posZ))
        # print("---------------- DONT SET MOLANG ----------------")
        # return
        SetBlockEntityMolangValue(
            (event.posX, event.posY, event.posZ),
            "variable.mod_block_facing",
            aux & 0b111,
        )

can_play_animation = False

@UiInitFinishedEvent.Listen()
def onUIInitFinished(event):
    # type: (UiInitFinishedEvent) -> None
    global can_play_animation
    can_play_animation = True


@DiggerUpdateCrack.Listen()
def onUpdateCrack(event):
    # type: (DiggerUpdateCrack) -> None
    # WARNING: 调用不当将导致游戏强制中断
    global can_play_animation
    if not GetBlockName((event.x, event.y, event.z)):
        print("[WARN] Digger crack was too early to set, may crash game")
        return
    if can_play_animation:
        SetCrackFrame(event.dim, (event.x, event.y, event.z), event.level)
