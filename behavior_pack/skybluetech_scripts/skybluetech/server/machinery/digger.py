# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.define.block import BlockBasicInfo
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
)

from ...common.define import flags
from ...common.define.id_enum import Machinery, Upgraders
from ...common.events.machinery.digger import (
    DiggerUpdateCrack,
    DiggerWorkModeUpdatedEvent,
)
from ...common.machinery_def.digger import (
    K_FRONT_BLOCK_AUX,
    K_FRONT_BLOCK_ID,
    STORE_RF_MAX,
)
from ...common.utils.block_sync import BlockSync
from .basic import (
    GUIControl,
    UpgradeControl,
    WorkRenderer,
)
from .core import RegisterMachine

TICKS_PER_SECOND = 20
block_sync = BlockSync(Machinery.DIGGER, side=BlockSync.SIDE_SERVER)
block_basic_info_cache = {}  # type: dict[str, BlockBasicInfo]


@RegisterMachine
class Digger(WorkRenderer, UpgradeControl, GUIControl):
    block_name = Machinery.DIGGER
    dump_progress_to_block_entity_data = True
    item_input_slots = ()
    item_output_slots = (0,)
    store_rf_max = STORE_RF_MAX
    running_power = 40
    upgrade_slot_start = 1
    upgrade_slots = 4
    allow_upgraders = frozenset({
        Upgraders.BASIC_SPEED_UPGRADER,
        Upgraders.BASIC_ENERGY_UPGRADER,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Digger, self).__init__(dim, x, y, z, block_entity_data)
        self.dx, self.dy, self.dz = GetOppositeDirFromFacing(
            CF.CreateBlockState(LEVEL_ID).GetBlockStates(
                (x, y, z),
                self.dim,
            )["minecraft:facing_direction"]
        )
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
            (x + self.dx, y + self.dy, z + self.dz),
            self.dim,
        )
        self._front_block, self._front_block_aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])  # block is None?
        self.prev_crack_stage = 0
        self.handler.SubscribeOnPlaced(self._digger_on_placed)
        self.handler.SubscribeOnTicking(self._digger_on_ticking)
        self.handler.SubscribeOnNeighborChanged(self._digger_on_neighbor_changed)
        self.handler.SubscribeOnUnload(self._digger_on_unload)
        self.handler.SubscribeOnWorkStatusUpdated(self._digger_on_work_status_updated)
        # NOTE: 我们假设方块之后的朝向直到方块被销毁前都不会变化

    def _digger_on_placed(self, _):
        self.start_next()

    def _digger_on_ticking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.run_once()
                self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            else:
                crack_stage = int(self.GetProcessProgress() * 10)
                if crack_stage != self.prev_crack_stage:
                    self.prev_crack_stage = crack_stage
                    self.update_crack_frame_to_client()
                break

    def _digger_on_neighbor_changed(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if (
            event.neighborPosX - self.x == self.dx
            and event.neighborPosY - self.y == self.dy
            and event.neighborPosZ - self.z == self.dz
        ):
            self.start_next((event.toBlockName, event.toAuxValue))

    def _digger_on_unload(self):
        # type: () -> None
        block_sync.discard_block((self.dim, self.x, self.y, self.z))


    def _digger_on_work_status_updated(self):
        DiggerWorkModeUpdatedEvent(self.x, self.y, self.z, self.IsActive()).sendMulti(
            block_sync.get_players((self.dim, self.x, self.y, self.z))
        )

    def start_next(self, new_block=None):
        # type: (tuple[str, int] | None) -> None
        if new_block:
            block_name, block_aux = new_block
        else:
            block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                (self.x + self.dx, self.y + self.dy, self.z + self.dz),
                self.dim,
            )
            block_name, block_aux = (None, 0) if block_data is None else (block_data["name"], block_data["aux"])
        self.front_block = block_name
        self.front_block_aux = block_aux
        if block_name is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        basic = block_basic_info_cache.get(block_name)
        if basic is None:
            basic = block_basic_info_cache[block_name] = BlockBasicInfo.unmarshal(
                CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(block_name)
            )
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

    def run_once(self):
        CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
            (self.x + self.dx, self.y + self.dy, self.z + self.dz),
            {"name": "minecraft:air", "aux": 0},
            1,
            dimensionId=self.dim,
        )
        self.collect()

    def collect(self):
        item_uqids = CF.CreateEntityComponent("").GetEntitiesBySelector("@e[type=item,x=%d,y=%d,z=%d,r=1.5]"
            % (self.x + self.dx, self.y + self.dy, self.z + self.dz))
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
                    (self.x - self.dx, self.y - self.dy, self.z - self.dz),
                )

    def update_crack_frame_to_client(self):
        DiggerUpdateCrack(
            self.dim,
            self.x + self.dx,
            self.y + self.dy,
            self.z + self.dz,
            self.prev_crack_stage,
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    @property
    def front_block(self):
        # type: () -> str | None
        return self._front_block

    @front_block.setter
    def front_block(self, value):
        # type: (str | None) -> None
        self.bdata[K_FRONT_BLOCK_ID] = self._front_block = value

    @property
    def front_block_aux(self):
        # type: () -> int
        return self._front_block_aux

    @front_block_aux.setter
    def front_block_aux(self, value):
        # type: (int) -> None
        self.bdata[K_FRONT_BLOCK_AUX] = self._front_block_aux = value


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
