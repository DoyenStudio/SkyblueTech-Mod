# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import PlayerUseItemToPos, MayPlace
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    UpdateBlockStates,
    GetBlockStates,
    GetBlockName,
    SetBlock,
    GetPlayerDimensionId,
    GetBlockAuxValueFromStates,
    GetBlockPaletteBetweenPos,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.id_enum import WIND_GENERATOR as MACHINE_ID, Paddle
from ...common.define.facing import DXYZ_FACING, FACING_EN
from ...common.events.machinery.wind_generator import (
    WindGeneratorStatesRequest,
    WindGeneratorStatesUpdate,
)
from ...common.machinery_def.wind_generator import get_paddle_output, item2paddle
from ...common.ui_sync.machinery.wind_generator import WindGeneratorUISync
from ...common.utils.block_sync import BlockSync
from ..transmitters.wire.logic import isWire
from .basic import BaseGenerator, ItemContainer, GUIControl, RegisterMachine
from .pool import GetMachineStrict

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class WindGenerator(BaseGenerator, ItemContainer, GUIControl):
    block_name = MACHINE_ID
    store_rf_max = 14400
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    input_slots = (0,)
    output_slots = ()

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = WindGeneratorUISync.NewServer(self).Activate()
        self.t = 0
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("WindGenerator BlockState None")
        self.facing = states["minecraft:cardinal_direction"]  # type: str
        self.layer = states["skybluetech:layer"]  # type: int
        # 如果不是基座方块则无功能
        self.is_base_block = self.layer == 0
        self.max_mcw = 0.0
        self.actual_mcw = 0.0
        self.power_output = 0
        self.rot_speed = 0.0
        self._cached_paddle_type = None
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        if self.is_base_block:
            GUIControl.OnClick(self, event)
        else:
            event.cancel()
            PlayerUseItemToPos(event.playerId, (self.x, self.y - self.layer, self.z), 2)

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        if not self.is_base_block:
            return
        self.t += 1
        if self.t % 80 == 0:
            self.reduce_dura()
            self.update_power()
        if self.t % 5 == 0 and self.IsActive():
            self.OnSync()

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        block_id = event.fullName
        dim = event.dimensionId
        x = event.x
        y = event.y
        z = event.z
        facing = event.face
        if not MayPlace(block_id, (x, y + 1, z), facing, dim) or not MayPlace(
            block_id, (x, y + 2, z), facing, dim
        ):
            event.cancel()

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        if not self.is_base_block:
            return
        states = {}
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isWire(bname)
            states["skybluetech:connection_" + facing_en] = connectToWire
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            states,
        )
        for i in range(1, 3):
            SetBlock(
                self.dim,
                (self.x, self.y + i, self.z),
                self.block_name,
                GetBlockAuxValueFromStates(self.block_name, {"skybluetech:layer": i}),
            )

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if not self.is_base_block:
            return
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        connectToWire = isWire(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire},
        )
        ExecLater(
            0,
            lambda: WindGeneratorStatesUpdate(
                self.x, self.y, self.z, None, self.rot_speed
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z))),
        )

    def OnSync(self):
        if not self.is_base_block:
            self.sync.MarkedAsChanged()
            return
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.mcw = self.actual_mcw
        self.sync.power = self.power_output
        self.sync.MarkedAsChanged()

    def OnDestroy(self):
        base_y = self.y - self.layer
        for i in range(3):
            if i == 0:
                m = GetMachineStrict(self.dim, self.x, base_y + i, self.z)
                if isinstance(m, ItemContainer):
                    m.DropAllItems()
            if i != self.layer:
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    @SuperExecutorMeta.execute_super
    def OnSlotUpdate(self, slot_pos):
        if slot_pos == 0:
            self._cached_paddle_type = None
        if self.paddle_type != WindGeneratorStatesUpdate.PADDLE_EMPTY:
            if self.HasDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT):
                self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        self.update_power()
        ExecLater(
            0,
            lambda: WindGeneratorStatesUpdate(
                self.x, self.y, self.z, self.paddle_type, self.rot_speed
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z))),
        )

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return "skybluetech:wind_generator_paddle" in item.GetBasicInfo().tags

    def reduce_dura(self):
        paddle = self.GetSlotItem(0, get_user_data=True)
        if paddle is None or paddle.durability is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        paddle.durability -= 1
        if paddle.durability <= 0:
            self.SetSlotItem(0, None)
        else:
            self.SetSlotItem(0, paddle)

    def update_power(self):
        if self.paddle_type == WindGeneratorStatesUpdate.PADDLE_EMPTY:
            self.max_mcw = 0
        else:
            self.max_mcw = max(0, min(256, self.y - 40)) / 4
        self.actual_mcw = int(self.max_mcw * self.get_actual_output_pc())
        self.power_output = int(
            self.actual_mcw / 2 * get_paddle_output(self.paddle_type)
        )
        if self.max_mcw > 0:
            self.rot_speed = float(self.actual_mcw) / 5120 + 0.01
        else:
            self.rot_speed = 0
        self.OnSync()
        self.SetOutputPower(self.output_power)

    def get_actual_output_pc(self):
        if self.facing == "north" or self.facing == "south":
            pos1 = (self.x - 2, self.y, self.z - 10)
            pos2 = (self.x + 2, self.y + 4, self.z + 10)
        elif self.facing == "east" or self.facing == "west":
            pos1 = (self.x - 10, self.y, self.z - 2)
            pos2 = (self.x + 10, self.y + 4, self.z + 2)
        else:
            print("[WindGenerator] facing error: %s" % self.facing)
            return 0
        vol = (pos2[0] - pos1[0]) * (pos2[1] - pos1[1]) * (pos2[2] - pos1[2])
        pal = GetBlockPaletteBetweenPos(self.dim, pos1, pos2, eliminateAir=False)
        air_count = pal.GetBlockCountInBlockPalette("minecraft:air")
        if pal.GetBlockCountInBlockPalette("minecraft:air") < vol * 0.6:
            return 0
        return float(air_count + 3) / vol

    @property
    def paddle_type(self):
        if self._cached_paddle_type is None:
            slotitem = self.GetSlotItem(0)
            if slotitem is None:
                self._cached_paddle_type = WindGeneratorStatesUpdate.PADDLE_EMPTY
            else:
                self._cached_paddle_type = item2paddle(slotitem.id)
        return self._cached_paddle_type


@WindGeneratorStatesRequest.Listen()
def onRecvRequest(event):
    # type: (WindGeneratorStatesRequest) -> None
    m = GetMachineStrict(
        GetPlayerDimensionId(event.player_id), event.x, event.y, event.z
    )
    if not isinstance(m, WindGenerator) or not m.is_base_block:
        return
    WindGeneratorStatesUpdate(
        event.x, event.y, event.z, m.paddle_type, m.rot_speed
    ).send(event.player_id)
