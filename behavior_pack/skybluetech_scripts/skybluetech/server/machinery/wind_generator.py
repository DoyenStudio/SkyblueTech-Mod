# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)

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
from .basic import BaseGenerator, GUIControl, ItemContainer
from .core import RegisterMachine
from .core.pool import GetLoadedMachine
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(wire=True)

block_sync = BlockSync(Machinery.WIND_GENERATOR, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class WindGenerator(GUIControl, ItemContainer, BaseGenerator):
    block_name = Machinery.WIND_GENERATOR
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    item_input_slots = (0,)
    item_output_slots = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        super(WindGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self.t = 0
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates((self.x, self.y, self.z), self.dim)
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
        self.handler.UnsubscribeOnClick(self._gui_control_on_click)
        self.handler.SubscribeOnClick(self._wind_generator_on_click)
        self.handler.SubscribeOnTicking(self._wind_generator_on_ticking)
        self.handler.SubscribeOnPlaced(self._wind_generator_on_placed)
        self.handler.SubscribeOnNeighborChanged(self._wind_generator_on_neighbor_changed)
        self.handler.SubscribeOnDestroy(self._wind_generator_on_destroy)
        self.handler.SubscribeOnUnload(self._wind_generator_on_unload)
        self.handler.SubscribeOnSlotUpdate(self._wind_generator_on_slot_update)

    def _wind_generator_on_click(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        if self.is_base_block:
            GUIControl._gui_control_on_click(self, event)
        else:
            event.cancel()
            CF.CreateBlockInfo(event.playerId).PlayerUseItemToPos(
                (self.x, self.y - self.layer, self.z),
                2,
            )

    def _wind_generator_on_ticking(self):
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
        if not CF.CreateBlockInfo(LEVEL_ID).MayPlace(
            block_id,
            (x, y + 1, z),
            facing,
            dim,
        ) or not CF.CreateBlockInfo(LEVEL_ID).MayPlace(
            block_id,
            (x, y + 2, z),
            facing,
            dim,
        ):
            event.cancel()

    def _wind_generator_on_placed(self, _):
        if not self.is_base_block:
            return
        TCON.block_placed(self)
        for i in range(1, 3):
            CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                (self.x, self.y + i, self.z),
                {"name": self.block_name, "aux": CF.CreateBlockState(LEVEL_ID).GetBlockAuxValueFromStates(self.block_name, {"skybluetech:layer": i})},
                0,
                dimensionId=self.dim,
            )

    def _wind_generator_on_neighbor_changed(self, event):
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

    def _wind_generator_on_destroy(self):
        base_y = self.y - self.layer
        for i in range(3):
            if i == 0:
                m = GetLoadedMachine(self.dim, self.x, base_y + i, self.z)
                if isinstance(m, ItemContainer):
                    m.DropAllItems()
            if i != self.layer:
                pos = (self.x, base_y + i, self.z)
                if (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
                    pos,
                    self.dim,
                ) or {}).get("name") == self.block_name:
                    CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
                        pos,
                        {"name": "minecraft:air", "aux": 0},
                        0,
                        dimensionId=self.dim,
                    )

    def _wind_generator_on_unload(self):
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def _wind_generator_on_slot_update(self, slot_pos):
        if slot_pos == 0:
            self._cached_paddle_type = None
        # 叶片槽空了立即显示缺少输入, 不用等下一次耐久结算 (reduce_dura)
        self.UpdateDeactiveFlag(
            flags.DEACTIVE_FLAG_NO_INPUT,
            self.paddle_type == WindGeneratorStatesUpdate.PADDLE_EMPTY,
        )
        self.update_power()
        ExecLater(
            0,
            lambda: WindGeneratorStatesUpdate(
                self.x, self.y, self.z, self.paddle_type, self.rot_speed
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z))),
        )

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            self._wind_generator_is_valid_input(slot, item),
        )
        return all(results)

    def _wind_generator_is_valid_input(self, slot, item):
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
        # 有叶片但没有风力输出 (高度不超过 40 / 扫风范围内空气不足六成) 时状态灯显示待机;
        # 缺叶片仍是 NO_INPUT, 由槽位更新与 reduce_dura 管理
        self.UpdateDeactiveFlag(
            flags.DEACTIVE_FLAG_NO_RECIPE,
            self.paddle_type != WindGeneratorStatesUpdate.PADDLE_EMPTY and self.power_output <= 0,
        )

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
        pal = CF.CreateBlock(LEVEL_ID).GetBlockPaletteBetweenPos(
            self.dim,
            pos1,
            pos2,
            eliminateAir=False,
        )
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
    m = GetLoadedMachine(
        CF.CreateDimension(event.player_id).GetEntityDimensionId(), event.x, event.y, event.z
    )
    if not isinstance(m, WindGenerator) or not m.is_base_block:
        return
    WindGeneratorStatesUpdate(
        event.x, event.y, event.z, m.paddle_type, m.rot_speed
    ).send(event.player_id)
