# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.server import PlayerUseItemToPos, MayPlace
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ClientBlockUseEvent,
)
from skybluetech_scripts.tooldelta.api.timer import ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    UpdateBlockStates,
    GetBlockStates,
    GetBlockName,
    SetBlock,
    GetPlayerDimensionId,
    GetPlayersInDim,
    GetBlockAuxValueFromStates,
    GetBlockPaletteBetweenPos,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockNameAndAux,
    SetBlockEntityMolangValue,
)
from ..define.events.wind_generator import (
    WindGeneratorStatesRequest,
    WindGeneratorStatesUpdate,
)
from ..define.id_enum.machinery import WIND_GENERATOR as MACHINE_ID
from ..utils.constants import DXYZ_FACING, FACING_EN
from ..ui_sync.machines.wind_generator import WindGeneratorUISync
from ..transmitters.wire.logic import isWire
from .basic import AutoSaver, BaseMachine, ItemContainer, GUIControl, RegisterMachine
from .pool import GetMachineStrict


@RegisterMachine
class WindGenerator(AutoSaver, BaseMachine, ItemContainer, GUIControl):
    block_name = MACHINE_ID
    store_rf_max = 14400
    energy_io_mode = (1, 1, 1, 1, 1, 1)
    input_slots = ()
    output_slots = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        AutoSaver.__init__(self, dim, x, y, z, block_entity_data)
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = WindGeneratorUISync.NewServer(self).Activate()
        self.t = 0
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("WindGenerator BlockState None")
        self.facing = states["minecraft:cardinal_direction"] # type: str
        self.layer = states["skybluetech:layer"] # type: int
        # 如果不是基座方块则无功能
        self.is_base_block = self.layer == 0
        self.update_power()


    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        if self.is_base_block:
            GUIControl.OnClick(self, event)
        else:
            event.cancel()
            PlayerUseItemToPos(event.playerId, (self.x, self.y - self.layer, self.z), 2)

    def OnTicking(self):
        if not self.is_base_block:
            return
        if self.t % 5 == 0 and self.IsActive():
            self.AddPower(self.power_output * 5, True)
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
        if (
            not MayPlace(block_id, (x, y + 1, z), facing, dim)
            or not MayPlace(block_id, (x, y+2, z), facing, dim)
        ):
            event.cancel()

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
                (self.x, self.y+i, self.z),
                self.block_name,
                GetBlockAuxValueFromStates(
                    self.block_name,
                    {"skybluetech:layer": i}
                )
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
        ExecLater(0, lambda:WindGeneratorStatesUpdate(
            self.x, self.y, self.z, self.rot_speed
        ).sendMulti(GetPlayersInDim(self.dim)))

    def update_power(self):
        self.max_mcw = max(0, min(256, self.y - 40)) / 4
        self.actual_mcw = int(self.max_mcw * self.get_actual_output_pc())
        self.power_output = int(self.actual_mcw / 2)
        self.rot_speed = float(self.actual_mcw) / 640
        self.OnSync()

    def get_actual_output_pc(self):
        if self.facing == "north" or self.facing == "south":
            pos1 = (self.x - 2, self.y, self.z - 20)
            pos2 = (self.x + 2, self.y + 4, self.z + 20)
        elif self.facing == "east" or self.facing == "west":
            pos1 = (self.x - 20, self.y, self.z - 2)
            pos2 = (self.x + 20, self.y + 4, self.z + 2)
        else:
            print("[WindGenerator] facing error: %s" % self.facing)
            return 0
        vol = (pos2[0] - pos1[0]) * (pos2[1] - pos1[1]) * (pos2[2] - pos1[2])
        pal = GetBlockPaletteBetweenPos(
            self.dim, pos1, pos2, eliminateAir=False
        )
        air_count = pal.GetBlockCountInBlockPalette("minecraft:air")
        if pal.GetBlockCountInBlockPalette("minecraft:air") < vol * 0.6:
            return 0
        return float(air_count + 3) / vol

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
            if i != self.layer:
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        AutoSaver.OnUnload(self)
        GUIControl.OnUnload(self)


@WindGeneratorStatesRequest.Listen()
def onRecvRequest(event):
    # type: (WindGeneratorStatesRequest) -> None
    m = GetMachineStrict(
        GetPlayerDimensionId(event.player_id),
        event.x, event.y, event.z
    )
    if not isinstance(m, WindGenerator) or not m.is_base_block:
        return
    WindGeneratorStatesUpdate(
        event.x, event.y, event.z, m.rot_speed
    ).send(event.player_id)


# CLIENT PART

def updateBlockRender(x, y, z):
    # type: (int, int, int) -> None
    _, aux = GetBlockNameAndAux((x, y, z))
    facing = aux & 0b11
    layer  = (aux & 0b1100) >> 2
    is_conn_west  = bool(aux & 0b00010000)
    is_conn_south = bool(aux & 0b00100000)
    is_conn_north  = bool(aux & 0b01000000)
    is_conn_east = bool(aux & 0b10000000)
    if layer != 0:
        return
    for molang_name, value in (
        ("variable.mod_is_base_block", 1),
        ("variable.mod_block_facing", facing),
        ("variable.is_connect_east", is_conn_east),
        ("variable.is_connect_south", is_conn_south),
        ("variable.is_connect_west", is_conn_west),
        ("variable.is_connect_north", is_conn_north),
    ):
        SetBlockEntityMolangValue(
            (x, y, z),
            molang_name,
            value,
        )

@ClientBlockUseEvent.Listen(inner_priority=10)
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName != WindGenerator.block_name:
        return
    _, aux = GetBlockNameAndAux((event.x, event.y, event.z))
    layer  = (aux & 0b1100) >> 2
    if layer != 0:
        # 只改变 GUI 读取到的 xyz。。
        event.y -= layer

@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName != WindGenerator.block_name:
        return
    updateBlockRender(event.posX, event.posY, event.posZ)
    WindGeneratorStatesRequest(
        event.posX, event.posY, event.posZ
    ).send()

@WindGeneratorStatesUpdate.Listen()
def onStateUpdated(event):
    # type: (WindGeneratorStatesUpdate) -> None
    SetBlockEntityMolangValue(
        (event.x, event.y, event.z),
        "variable.mod_anim_speed",
        event.rot_speed,
    )
    updateBlockRender(event.x, event.y, event.z)

