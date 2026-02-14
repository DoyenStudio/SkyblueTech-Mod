# coding=utf-8
import uuid
from mod.server.blockEntityData import BlockEntityData
from mod.server.extraServerApi import GetLevelId
from skybluetech_scripts.tooldelta.events.server import (
    ServerEntityTryPlaceBlockEvent,
    ServerBlockUseEvent,
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockAuxValueFromStates,
    GetBlockName,
    GetBlockStates,
    GetBlockEntityData,
    GetPlayerDimensionId,
    SetBlock,
    UpdateBlockStates,
    CleanExtraData,
    GetExtraData,
    SetExtraData,
    MayPlace,
    PlayerUseItemToPos,
)
from skybluetech_scripts.tooldelta.api.client import (
    CreateShapeFactory,
    GetBlockNameAndAux,
    GetBlockEntityData as CGetBlockEntityData,
)

from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.tooldelta.utils.nbt import NBT2Py
from ..define import flags
from ..define.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
    RFRepeaterPlantBuildAddWire,
    RFRepeaterPlantSettingsUpdate,
    RFRepeaterPlantSettingUpload,
)
from ..define.id_enum.machinery import RF_REPEATER_PLANT as MACHINE_ID
from ..define.facing import DXYZ_FACING, FACING_EN
from ..utils.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from ..ui.machinery.rf_repeater_plant import RFRepeaterPlantUI
from ..ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ..transmitters.wire.logic import isWire
from ..utils.block_sync import BlockSync
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict

# TYPE CHECKING
if 0:
    from mod.client.component.drawingShapeCompClient import DrawingShapeCompClient
# TYPE CHECKING END

K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"

K_NETWORK_DIM = "dim"
K_NETWORK_NODES = "nodes"

K_MODE = "mode"
K_BOUND_NETWORK_UUID = "bound_nuuid"
K_CONNECT_NODES = "con_nodes"

block_sync = BlockSync(MACHINE_ID)


@RegisterMachine
class RFRepeaterPlant(BaseMachine, GUIControl, ItemContainer):
    bound_ui = RFRepeaterPlantUI
    block_name = MACHINE_ID
    store_rf_max = 100000
    energy_io_mode = (1, 1, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = RFRepeaterPlantUISync.NewServer(self).Activate()
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("RFRepeaterPlant BlockState None")
        self.facing = states["minecraft:cardinal_direction"]  # type: str
        self.layer = states["skybluetech:layer"]  # type: int
        # 如果不是基座方块则无功能
        self.is_base_block = self.layer == 0

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

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        if not self.is_base_block:
            event.cancel()
            PlayerUseItemToPos(event.playerId, (self.x, self.y - self.layer, self.z), 2)
            return
        node_data = get_node_data(self.dim, self.x, self.y, self.z)
        if node_data is None:
            mode = 0b1111
        else:
            mode = node_data[K_MODE]
        east_io_mode, west_io_mode, south_io_mode, north_io_mode = get_mode(mode)
        network_prof_data = sum_network_data(
            (node_data or {}).get(K_BOUND_NETWORK_UUID)
        )
        GUIControl.OnClick(
            self,
            event,
            {
                "st:init_content": RFRepeaterPlantSettingsUpdate(
                    self.dim,
                    self.x,
                    self.y,
                    self.z,
                    east_io_mode,
                    west_io_mode,
                    south_io_mode,
                    north_io_mode,
                    network_prof_data.network_plant_count,
                    network_prof_data.network_plant_online_count,
                    network_prof_data.total_output_count,
                    network_prof_data.total_output_active_count,
                    network_prof_data.total_input_count,
                    network_prof_data.total_input_active_count,
                ).marshal()
            },
        )

    def OnPlaced(self, event):
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
        add_single_node(self.dim, self.x, self.y, self.z)

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
            {"skybluetech:%s_charge" % facing_en: connectToWire},
        )

    def OnDestroy(self):
        remove_node_and_flush(self.dim, self.x, self.y, self.z)
        base_y = self.y - self.layer
        for i in range(3):
            if i != self.layer:
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def get_nearconn_plants(self):
        # type: () -> list[tuple[int, int, int]] | None
        node_data = get_nodes_data().get((self.dim, self.x, self.y, self.z))
        if node_data is None:
            return None
        return node_data[K_CONNECT_NODES]


build_speed_limiter = PlayerRateLimiter(1)


class SummariedNetworkData:
    def __init__(self, network_uuid):
        self.network_uuid = network_uuid
        self.network_plant_count = 0
        self.network_plant_online_count = 0
        self.total_output_count = 0
        self.total_output_active_count = 0
        self.total_input_count = 0
        self.total_input_active_count = 0
        self.init()

    def init(self):
        network_data = get_networks_data().get(self.network_uuid)
        if network_data is None:
            return
        dim = network_data[K_NETWORK_DIM]
        nodes = get_nodes_in_network(self.network_uuid)
        self.network_plant_count = len(nodes)
        for (x, y, z), io_mode in nodes.items():
            east, west, south, north = get_mode(io_mode)
            self.total_input_count += 4 - (east + west + south + north)
            self.total_output_count += east + west + south + north
            if isinstance(GetMachineStrict(dim, x, y, z), RFRepeaterPlant):
                self.network_plant_online_count += 1
                self.total_input_active_count += 4 - (east + west + south + north)
                self.total_output_active_count += east + west + south + north


@RFRepeaterPlantBuildRequest.Listen()
def onEstablishConn(event):
    # type: (RFRepeaterPlantBuildRequest) -> None
    if not build_speed_limiter.record(event.player_id):
        RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_TOO_FAST).send(
            event.player_id
        )
        return
    dim = GetPlayerDimensionId(event.player_id)
    start_m = GetMachineStrict(dim, event.x, event.y, event.z)
    if not isinstance(start_m, RFRepeaterPlant) or not start_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_START
        ).send(event.player_id)
        return
    end_m = GetMachineStrict(dim, event.to_x, event.to_y, event.to_z)
    if not isinstance(end_m, RFRepeaterPlant) or not end_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_END
        ).send(event.player_id)
        return
    start_pos = (event.x, event.y, event.z)
    end_pos = (event.to_x, event.to_y, event.to_z)
    start_nearby_nodes = start_m.get_nearconn_plants()
    end_nearby_nodes = end_m.get_nearconn_plants()
    if start_nearby_nodes is None or end_nearby_nodes is None:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR
        ).send(event.player_id)
        return
    elif start_pos in end_nearby_nodes or end_pos in start_nearby_nodes:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_ALREADY_CONNECTED
        ).send(event.player_id)
        return
    elif start_pos == end_pos:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_CANT_CONNECT_SELF
        ).send(event.player_id)
        return
    if (
        hypot(
            start_pos[0] - end_pos[0],
            start_pos[1] - end_pos[1],
            start_pos[2] - end_pos[2],
        )
        > 64
    ):
        RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_TOO_FAR).send(
            event.player_id
        )
        return
    res = build_connection(dim, start_pos, end_pos)
    if not res:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR2
        ).send(event.player_id)
        return
    RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_SUCC).send(
        event.player_id
    )
    RFRepeaterPlantBuildAddWire(
        event.x, event.y, event.z, event.to_x, event.to_y, event.to_z
    ).sendMulti(block_sync.get_players((dim,) + start_pos))


@RFRepeaterPlantSettingUpload.Listen()
def onSettingUpload(event):
    # type: (RFRepeaterPlantSettingUpload) -> None
    dim = GetPlayerDimensionId(event.player_id)
    m = GetMachineStrict(dim, event.x, event.y, event.z)
    if not isinstance(m, RFRepeaterPlant):
        print("no")
        return
    if not m.is_base_block:
        print("no 2")
        return
    if event.io_dir < 0 or event.io_dir > 3:
        print("no 3")
        return
    print("upload io mode", event.io_mode)
    change_node_mode(
        dim,
        event.x,
        event.y,
        event.z,
        single_dir=event.io_dir,
        single_mode=bool(event.io_mode),
    )
    print("really changed", event.io_mode)


def sum_network_data(network_uuid):
    return SummariedNetworkData(network_uuid)


def set_mode(east, west, south, north):
    # type: (bool, bool, bool, bool) -> int
    return east << 3 | west << 2 | south << 1 | north


def get_mode(mode):
    # type: (int) -> tuple[bool, bool, bool, bool]
    return (
        bool(mode >> 3 & 1),
        bool(mode >> 2 & 1),
        bool(mode >> 1 & 1),
        bool(mode & 1),
    )


def hypot(*dis):
    # type: (float) -> float
    return sum(i**2 for i in dis) ** 0.5


def get_networks_data():
    return GetExtraData(GetLevelId(), K_GLOBAL_NETWORK_DATAS, {})


def save_networks_data(networks_data):
    # type: (dict[str, dict]) -> None
    SetExtraData(GetLevelId(), K_GLOBAL_NETWORK_DATAS, networks_data)


def get_node_data(dim, x, y, z):
    # type: (int, int, int, int) -> dict | None
    return get_nodes_data().get((dim, x, y, z))


def get_nodes_data():
    # type: () -> dict[tuple[int, int, int, int], dict]
    return GetExtraData(GetLevelId(), K_GLOBAL_NODES, {})


def save_nodes_data(nodes_data):
    # type: (dict[tuple[int, int, int, int], dict]) -> None
    SetExtraData(GetLevelId(), K_GLOBAL_NODES, nodes_data)


def get_node_bound_network(dim, x, y, z):
    # type: (int, int, int, int) -> str | None
    res = get_nodes_data().get((dim, x, y, z))
    if res is None:
        return None
    return res[K_BOUND_NETWORK_UUID]


def get_nodes_in_network(network_uuid):
    # type: (str) -> dict[tuple[int, int, int], int]
    network_data = get_networks_data().get(network_uuid)
    if not network_data:
        return {}
    return network_data[K_NETWORK_NODES]


def add_single_node(dim, x, y, z):
    # type: (int, int, int, int) -> None
    network_uuid = _add_node_to_network(dim, x, y, z)
    bedata = GetBlockEntityData(dim, x, y, z)
    if bedata is not None:
        bedata[K_BOUND_NETWORK_UUID] = network_uuid
        bedata[K_CONNECT_NODES] = []


def build_connection(
    dim,  # type: int
    node,  # type: tuple[int, int, int]
    node2,  # type: tuple[int, int, int]
):
    nodes_data = get_nodes_data()
    networks_data = get_networks_data()
    x, y, z = node
    node_data = nodes_data.get((dim, x, y, z))
    if node_data is None:
        return False
    nx, ny, nz = node2
    node2_data = nodes_data.get((dim, nx, ny, nz))
    if node2_data is None:
        return False
    node2_data[K_CONNECT_NODES].append(node)
    node_data[K_CONNECT_NODES].append(node2)
    reinit_network_from_one_node(dim, x, y, z, networks_data, nodes_data)
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    bedata1 = GetBlockEntityData(dim, x, y, z)
    if bedata1 is not None:
        bedata1[K_CONNECT_NODES] = [list(i) for i in node_data[K_CONNECT_NODES]]
    bedata2 = GetBlockEntityData(dim, nx, ny, nz)
    if bedata2 is not None:
        bedata2[K_CONNECT_NODES] = [list(i) for i in node2_data[K_CONNECT_NODES]]
    return True


def change_node_mode(dim, x, y, z, new_modes=None, single_dir=None, single_mode=None):
    # type: (int, int, int, int, int | None, int | None, bool | None) -> None
    m = GetMachineStrict(dim, x, y, z)
    if not isinstance(m, RFRepeaterPlant):
        print("Retu")
        return
    orig = m.bdata[K_MODE] or 0b1111
    if new_modes is not None:
        m.bdata[K_MODE] = new_modes
    elif single_dir is not None and single_mode is not None:
        new_modes = m.bdata[K_MODE] = orig & ((1 << single_dir) ^ 0b1111) | (
            1 << single_dir if single_mode else 0
        )
    if new_modes is not None and single_dir is not None:
        print(
            "prev",
            bin(0b10000 | orig),
            "&",
            bin(0b10000 | 1 << single_dir),
            single_mode,
            "now",
            bin(0b10000 | new_modes),
        )
    network_uuid = m.bdata[K_BOUND_NETWORK_UUID]
    if network_uuid is None:
        print("giao")
        return
    networks_data = get_networks_data()
    network_data = networks_data.get(network_uuid)
    if network_data is None:
        print("[Error] RFRepeaterPlant: Network not found at {}".format((x, y, z)))
        return
    network_data[K_NETWORK_NODES][(x, y, z)] = new_modes
    nodes_data = get_nodes_data()
    nodes_data[(dim, x, y, z)][K_MODE] = new_modes
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    s = sum_network_data(network_uuid)
    east, west, south, north = get_mode(m.bdata[K_MODE])
    RFRepeaterPlantSettingsUpdate(
        dim,
        x,
        y,
        z,
        east,
        west,
        south,
        north,
        s.network_plant_count,
        s.network_plant_online_count,
        s.total_output_count,
        s.total_output_active_count,
        s.total_input_count,
        s.total_input_active_count,
    ).sendMulti(m.sync.GetPlayersInSync())


def remove_node_and_flush(dim, x, y, z):
    # type: (int, int, int, int) -> None
    nodes_data = get_nodes_data()
    node_data = nodes_data.pop((dim, x, y, z), None)
    if node_data is None:
        return
    nuuid = node_data[K_BOUND_NETWORK_UUID]
    if not nuuid:
        return
    near_nodes = node_data[K_CONNECT_NODES]
    networks_data = get_networks_data()
    _pop_node_from_network(dim, x, y, z, networks_data, nuuid)
    nodes_inited = set()
    for nx, ny, nz in near_nodes:
        _remove_connected_node(dim, nx, ny, nz, (x, y, z), nodes_data)
        reinit_network_from_one_node(
            dim, x, y, z, networks_data, nodes_data, nodes_inited
        )
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)


def reinit_network_from_one_node(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    networks_data,  # type: dict[str, dict]
    nodes_data,  # type: dict[tuple[int, int, int, int], dict]
    nodes_inited=None,  # type: set[tuple[int, int, int]] | None
):
    if nodes_inited is None:
        nodes_inited = set()
    if (dim, x, y, z) in nodes_inited:
        return
    network_data, nuuid = new_network(networks_data, dim)
    _dfs_reinit_network(dim, x, y, z, nodes_data, nuuid, network_data, nodes_inited)


def new_network(networks_dict, dim):
    # type: (dict[str, dict], int) -> tuple[dict, str]
    nuuid = uuid.uuid4().hex
    network_dict = networks_dict[nuuid] = {
        K_NETWORK_DIM: dim,
        K_NETWORK_NODES: {},
    }
    return network_dict, nuuid


def new_node_data(dim, x, y, z, bound_network_uuid):
    # type: (int, int, int, int, str) -> dict
    return {
        K_BOUND_NETWORK_UUID: bound_network_uuid,
        K_MODE: 0b0000,
        K_CONNECT_NODES: [],
    }


def _dfs_reinit_network(
    dim,  # type: int
    x,  # type: int
    y,  # type: int
    z,  # type: int
    nodes_data,  # type: dict[tuple[int, int, int, int], dict]
    nuuid,  # type: str
    network_data,  # type: dict[str, dict]
    nodes_inited,  # type: set[tuple[int, int, int]]
):
    if (x, y, z) in nodes_inited:
        return
    node_data = nodes_data.get((dim, x, y, z))
    if node_data is None:
        return
    node_data[K_BOUND_NETWORK_UUID] = nuuid
    network_data[K_NETWORK_NODES][(x, y, z)] = node_data[K_MODE]
    near_nodes = node_data[K_CONNECT_NODES]  # type: list[tuple[int, int, int]]
    nodes_inited.add((x, y, z))
    for node_x, node_y, node_z in near_nodes:
        _dfs_reinit_network(
            dim, node_x, node_y, node_z, nodes_data, nuuid, network_data, nodes_inited
        )


def _add_node_to_network(dim, x, y, z, network_uuid=None):
    # type: (int, int, int, int, str | None) -> str
    prev_networks = get_networks_data()
    nodes_data = get_nodes_data()
    if prev_networks is None:
        prev_networks = {}
    if network_uuid is None:
        network_data, network_uuid = new_network(prev_networks, dim)
    else:
        network_data = prev_networks[network_uuid]
    network_data[K_NETWORK_NODES][(x, y, z)] = 0b00
    nodes_data[(dim, x, y, z)] = new_node_data(dim, x, y, z, network_uuid)
    save_networks_data(prev_networks)
    save_nodes_data(nodes_data)
    return network_uuid


def _remove_connected_node(dim, x, y, z, nearby_node, nodes_data):
    # type: (int, int, int, int, tuple[int, int, int], dict[tuple[int, int, int, int], dict]) -> None
    node_data = nodes_data.get((dim, x, y, z))
    if node_data is None:
        return
    node_data[K_CONNECT_NODES].remove(nearby_node)


def _pop_node_from_network(dim, x, y, z, network_datas, network_uuid):
    # type: (int, int, int, int, dict[str, dict], str) -> None
    network_data = network_datas.get(network_uuid)
    if network_data is None:
        return
    del network_data[K_NETWORK_NODES][(x, y, z)]
    if not network_data[K_NETWORK_NODES]:
        del network_datas[network_uuid]


# CLIENT PART

lasers = {}  # type: dict[tuple[int, int, int], dict[tuple[int, int, int], Laser]]


class Laser:
    def __init__(self, start_pos, end_pos):
        # type: (tuple[float, float, float], tuple[float, float, float]) -> None
        x1, y1, z1 = self.start_pos = start_pos
        x2, y2, z2 = self.end_pos = end_pos
        self.shape = CreateShapeFactory().AddLineShape(
            (x1 + 0.5, y1 + 2.8, z1 + 0.5),
            (x2 + 0.5, y2 + 2.8, z2 + 0.5),
            hex2rgb(0x00FFFF),
        )

    def Remove(self):
        self.shape.Remove()

    def __hash__(self):
        return hash((self.start_pos, self.end_pos))

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, Laser):
            return False
        return self.start_pos == other.start_pos and self.end_pos == other.end_pos


def hex2rgb(hex):
    # type: (int) -> tuple[int, int, int]
    return (hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF


def add_laser(xyz1, xyz2):
    # type: (tuple[int, int, int], tuple[int, int, int]) -> None
    laser = Laser(xyz1, xyz2)
    lasers.setdefault(xyz1, {})[xyz2] = laser
    lasers.setdefault(xyz2, {})[xyz1] = laser


def remove_laser_src(xyz):
    # type: (tuple[int, int, int]) -> None
    pos_lasers = lasers.pop(xyz, None)
    if pos_lasers is None:
        return
    for other_xyz, laser in pos_lasers.copy().items():
        laser.Remove()
        other_pos_lasers = lasers.get(other_xyz)
        if other_pos_lasers is not None:
            other_pos_lasers.pop(xyz, None)
            if not other_pos_lasers:
                del lasers[other_xyz]


@ClientBlockUseEvent.Listen(inner_priority=10)
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName != MACHINE_ID:
        return
    _, aux = GetBlockNameAndAux((event.x, event.y, event.z))
    layer = (aux & 0b1100) >> 2
    if layer != 0:
        # 只改变 GUI 读取到的 xyz。。
        event.y -= layer


@asModBlockLoadedListener(MACHINE_ID)
def onPlantLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    block_entity_data = CGetBlockEntityData(event.posX, event.posY, event.posZ)
    if block_entity_data is None:
        return
    pydata = NBT2Py(block_entity_data["exData"])
    con_nodes = pydata.get(K_CONNECT_NODES, [])
    for con_node in con_nodes:
        add_laser((event.posX, event.posY, event.posZ), tuple(con_node))


@asModBlockRemovedListener(MACHINE_ID)
def onPlantUnloaded(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    remove_laser_src((event.posX, event.posY, event.posZ))


@RFRepeaterPlantBuildAddWire.Listen()
def onAddWire(event):
    # type: (RFRepeaterPlantBuildAddWire) -> None
    add_laser((event.x, event.y, event.z), (event.to_x, event.to_y, event.to_z))
