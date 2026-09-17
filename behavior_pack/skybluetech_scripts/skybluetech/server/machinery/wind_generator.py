# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockAuxValueFromStates,
    GetBlockName,
    GetBlockPaletteBetweenPos,
    GetBlockStates,
    GetPlayerDimensionId,
    MayPlace,
    PlayerUseItemToPos,
    SetBlock,
)
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.events.machinery.wind_generator import (
    WindGeneratorStatesRequest,
    WindGeneratorStatesUpdate,
)
from ...common.machinery_def.wind_generator import (
    FINAL_OUTPUT_POWER_MULTIPLIER,
    K_MCW,
    K_OUTPUT_POWER,
    MAX_MCW_HEIGHT_MULTIPLIER,
    STORE_RF_MAX,
    get_paddle_output,
    item2paddle,
)
from ...common.utils.block_sync import BlockSync
from .basic import BaseGenerator, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(wire=True)

block_sync = BlockSync(Machinery.WIND_GENERATOR, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class WindGenerator(BaseGenerator, ItemContainer, GUIControl):
    block_name = Machinery.WIND_GENERATOR
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    input_slots = (0,)
    output_slots = ()

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.t = 0
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("WindGenerator BlockState None")
        self.facing = states["minecraft:cardinal_direction"]  # type: str
        self.layer = states["skybluetech:layer"]  # type: int
        self.is_base_block = self.layer == 0
        self.max_mcw = 0.0
        self._actual_mcw = 0.0
        self._power_output = 0
        self.rot_speed = 0.0
        self._cached_paddle_type = None
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)
        else:
            self.update_power()

    def OnClick(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
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
        TCON.block_placed(self)
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
        TCON.neighbor_block_changed(self, event)
        ExecLater(
            0,
            lambda: WindGeneratorStatesUpdate(
                self.x, self.y, self.z, None, self.rot_speed
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z))),
        )

    def OnDestroy(self):
        base_y = self.y - self.layer
        for i in range(3):
            if i == 0:
                m = GetMachineStrict(self.dim, self.x, base_y + i, self.z)
                if isinstance(m, ItemContainer):
                    m.DropAllItems()
            if i != self.layer:
                pos = (self.x, base_y + i, self.z)
                if GetBlockName(self.dim, pos) == self.block_name:
                    SetBlock(self.dim, pos, "minecraft:air")

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
            self.max_mcw = max(0, min(256, self.y - 40)) * MAX_MCW_HEIGHT_MULTIPLIER
        self.actual_mcw = int(self.max_mcw * self.get_actual_output_pc())
        self.power_output = int(
            self.actual_mcw
            * FINAL_OUTPUT_POWER_MULTIPLIER
            * get_paddle_output(self.paddle_type)
        )
        if self.max_mcw > 0:
            self.rot_speed = float(self.actual_mcw) / 5120 + 0.01
        else:
            self.rot_speed = 0
        self.SetOutputPower(self.power_output)

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

    @property
    def actual_mcw(self):
        # type: () -> float
        return self._actual_mcw

    @actual_mcw.setter
    def actual_mcw(self, value):
        # type: (float) -> None
        self.bdata[K_MCW] = self._actual_mcw = value

    @property
    def power_output(self):
        # type: () -> int
        return self._power_output

    @power_output.setter
    def power_output(self, value):
        # type: (int) -> None
        self.bdata[K_OUTPUT_POWER] = self._power_output = value


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
