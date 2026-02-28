# coding=utf-8
import uuid
from mod.server.blockEntityData import BlockEntityData
from mod.server.extraServerApi import GetLevelId
from mod_log import logger
from skybluetech_scripts.tooldelta.events.server import (
    ServerEntityTryPlaceBlockEvent,
    ServerBlockUseEvent,
    BlockNeighborChangedServerEvent,
)
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
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ...common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
    RFRepeaterPlantBuildAddWire,
    RFRepeaterPlantSettingsUpdate,
    RFRepeaterPlantSettingUpload,
)
from ...common.define.id_enum.machinery import RF_REPEATER_PLANT as MACHINE_ID
from ...common.define.facing import DXYZ_FACING, FACING_EN
from ...common.define.ui_keys import RF_REPEATER_PLANT_UI
from ...common.ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ..transmitters.wire.logic import isWire
from ...common.machinery.utils.block_sync import BlockSync
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict


K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"


block_sync = BlockSync(MACHINE_ID)


@RegisterMachine
class RFRepeaterPlant(BaseMachine, GUIControl, ItemContainer):
    bound_ui = RF_REPEATER_PLANT_UI
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
        self.flush_data()

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
        node = get_node(self.dim, (self.x, self.y, self.z))
        if node is None:
            mode = 0b1111
            euid = "??????"
        else:
            mode = node.modes
            euid = node.bound_network_uuid[-6:]
        east_io_mode, west_io_mode, south_io_mode, north_io_mode = unpack_modes(mode)
        network_prof_data = sum_network_data(
            node.bound_network_uuid if node is not None else None
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
                    euid,
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
        add_single_node(self.dim, (self.x, self.y, self.z))

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

    def OnDestroy(self):
        remove_node_and_flush(self.dim, (self.x, self.y, self.z))
        base_y = self.y - self.layer
        for i in range(3):
            if i != self.layer:
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        ok = False
        if passed is not None:
            passed.add(self)
        for node_pos in self.nodes_in_network:
            plant = GetMachineStrict(self.dim, *node_pos)
            if not isinstance(plant, RFRepeaterPlant):
                continue
            if passed is not None and plant in passed:
                continue
            _ok, rf = plant.transfer_power_to(rf, max_limit, passed)
            ok = ok or _ok
            if rf == 0:
                return ok, 0
        return ok, rf

    def get_nearconn_plants(self):
        # type: () -> list[tuple[int, int, int]] | None
        node = get_node(self.dim, (self.x, self.y, self.z))
        if node is None:
            return None
        return node.connected_nodes

    def flush_data(self, from_network=None):
        # type: (NetworkData | None) -> None
        if from_network is not None:
            self.nodes_in_network = from_network.nodes
        else:
            my_node = get_node(self.dim, (self.x, self.y, self.z))
            self.nodes_in_network = {}
            if my_node is not None:
                network = get_network(my_node.bound_network_uuid)
                if network is not None:
                    self.nodes_in_network = network.nodes

    def transfer_power_to(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        requireWireModule()
        ok = False
        east, west, south, north = unpack_modes(self.modes)
        valid_output_faces = []  # type: list[int]
        if passed is not None:
            passed.add(self)
        if east:
            valid_output_faces.append(5)
        if west:
            valid_output_faces.append(4)
        if south:
            valid_output_faces.append(3)
        if north:
            valid_output_faces.append(2)
        cnode = GetContainerNode(self.dim, self.x, self.y, self.z, enable_cache=True)
        valid_output_networks = [
            v for k, v in cnode.inputs.items() if k in valid_output_faces
        ]
        for network in valid_output_networks:
            if network is None:
                continue
            for ap in network.get_input_access_points():
                machine = pool.GetMachineStrict(self.dim, *ap.target_pos)
                if machine is not None and not machine.is_non_energy_machine:
                    if passed is not None and machine in passed:
                        continue
                    updated, rf = machine.AddPower(rf, network.transfer_speed, passed)
                    ok = ok or updated
                    if rf == 0:
                        break
        return ok, rf

    @property
    def modes(self):
        # type: () -> int
        return self.bdata[NodeData.K_MODES] or 0b0000

    @modes.setter
    def modes(self, value):
        # type: (int) -> None
        print("SetMode", value)
        self.bdata[NodeData.K_MODES] = value


build_speed_limiter = PlayerRateLimiter(1)


class NetworkData(object):
    K_DIM = "dim"
    K_NODES = "nodes"

    def __init__(self, network_data, network_uuid):
        # type: (dict, str) -> None
        self.uuid = network_uuid
        self.dim = network_data[self.K_DIM]  # type: int
        self.nodes = network_data[self.K_NODES]  # type: dict[tuple[int, int, int], int]

    @classmethod
    def new(
        cls,
        dim,  # type: int
    ):
        return cls(
            {
                cls.K_DIM: dim,
                cls.K_NODES: {},
            },
            uuid.uuid4().hex,
        )

    def add_node(self, node_pos, modes=0b0000):
        # type: (tuple[int, int, int], int) -> None
        self.nodes[node_pos] = modes

    def remove_node(self, node_pos):
        # type: (tuple[int, int, int]) -> None
        self.nodes.pop(node_pos, None)

    def save_to_global_dict(self, network_datas):
        network_datas[self.uuid] = {
            self.K_DIM: self.dim,
            self.K_NODES: self.nodes,
        }


class NodeData(object):
    K_MODES = "modes"
    K_BOUND_NETWORK_UUID = "bound_nuuid"
    K_CONNECTED_NODES = "con_nodes"

    def __init__(self, dim, pos, node_data):
        # type: (int, tuple[int, int, int], dict) -> None
        self.dim = dim
        self.pos = pos
        self.bound_network_uuid = node_data[self.K_BOUND_NETWORK_UUID]  # type: str
        self.connected_nodes = node_data[self.K_CONNECTED_NODES]  # type: list[tuple[int, int, int]]
        self.modes = node_data[self.K_MODES]  # type: int

    @classmethod
    def new(
        cls,
        dim,  # type: int
        pos,  # type: tuple[int, int, int]
        bound_network_uuid,
    ):
        return cls(
            dim,
            pos,
            {
                cls.K_BOUND_NETWORK_UUID: bound_network_uuid,
                cls.K_MODES: 0b0000,
                cls.K_CONNECTED_NODES: [],
            },
        )

    def connect_to_node(self, node_pos):
        # type: (tuple[int, int, int]) -> None
        self.connected_nodes.append(node_pos)

    def disconnect_to_node(self, node_pos):
        # type: (tuple[int, int, int]) -> None
        self.connected_nodes.remove(node_pos)

    def save_to_global_dict(self, node_datas):
        x, y, z = self.pos
        node_datas[(self.dim, x, y, z)] = {
            self.K_BOUND_NETWORK_UUID: self.bound_network_uuid,
            self.K_MODES: self.modes,
            self.K_CONNECTED_NODES: self.connected_nodes,
        }
        # extra
        bdata = GetBlockEntityData(self.dim, x, y, z)
        if bdata is None:
            logger.error("RFRepeaterPlant: Failed to dump: {}".format(self.pos))
            return
        bdata[self.K_CONNECTED_NODES] = [[x, y, z] for x, y, z in self.connected_nodes]
        bdata[self.K_BOUND_NETWORK_UUID] = self.bound_network_uuid
        bdata[self.K_MODES] = self.modes


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
        network = get_network(self.network_uuid)
        if network is None:
            return
        self.network_plant_count = len(network.nodes)
        for (x, y, z), io_mode in network.nodes.items():
            east, west, south, north = unpack_modes(io_mode)
            self.total_input_count += 4 - (east + west + south + north)
            self.total_output_count += east + west + south + north
            if isinstance(GetMachineStrict(network.dim, x, y, z), RFRepeaterPlant):
                self.network_plant_online_count += 1
                self.total_input_active_count += 4 - (east + west + south + north)
                self.total_output_active_count += east + west + south + north


def requireWireModule():
    global GetContainerNode, pool
    if requireWireModule.has_cache:
        return
    from ..transmitters.wire.logic import logic_module
    from . import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False


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
        return
    if not m.is_base_block:
        return
    if event.io_dir < 0 or event.io_dir > 3:
        return
    change_node_mode(
        dim,
        event.x,
        event.y,
        event.z,
        single_dir=event.io_dir,
        single_mode=bool(event.io_mode),
    )


def sum_network_data(network_uuid):
    return SummariedNetworkData(network_uuid)


def pack_modes(east, west, south, north):
    # type: (bool, bool, bool, bool) -> int
    return east << 3 | west << 2 | south << 1 | north


def unpack_modes(mode):
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


def get_nodes_data():
    # type: () -> dict[tuple[int, int, int, int], dict]
    return GetExtraData(GetLevelId(), K_GLOBAL_NODES, {})


def save_nodes_data(nodes_data):
    # type: (dict[tuple[int, int, int, int], dict]) -> None
    SetExtraData(GetLevelId(), K_GLOBAL_NODES, nodes_data)


def get_node(dim, pos, global_nodes_data=None):
    # type: (int, tuple[int, int, int], dict | None) -> NodeData | None
    x, y, z = pos
    data = (global_nodes_data or get_nodes_data()).get((dim, x, y, z))
    if data is None:
        return None
    else:
        return NodeData(dim, pos, data)


def get_network(network_uuid, global_networks_data=None):
    # type: (str, dict | None) -> NetworkData | None
    data = (global_networks_data or get_networks_data()).get(network_uuid)
    if data is None:
        return None
    else:
        return NetworkData(data, network_uuid)


def add_single_node(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    _add_node_to_network(dim, pos)


def build_connection(
    dim,  # type: int
    node_pos1,  # type: tuple[int, int, int]
    node_pos2,  # type: tuple[int, int, int]
):
    nodes_data = get_nodes_data()
    networks_data = get_networks_data()
    node_1 = get_node(dim, node_pos1, nodes_data)
    if node_1 is None:
        return False
    node_2 = get_node(dim, node_pos2, nodes_data)
    if node_2 is None:
        return False
    # 移除原有网络数据, 因为要重新初始化网络
    _delete_network(networks_data, node_1.bound_network_uuid)
    _delete_network(networks_data, node_2.bound_network_uuid)
    node_1.connect_to_node(node_2.pos)
    node_2.connect_to_node(node_1.pos)
    node_1.save_to_global_dict(nodes_data)
    node_2.save_to_global_dict(nodes_data)
    _init_network_from_one_node(dim, node_pos1, networks_data, nodes_data)
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    return True


def change_node_mode(dim, x, y, z, new_modes=None, single_dir=None, single_mode=None):
    # type: (int, int, int, int, int | None, int | None, bool | None) -> None
    m = GetMachineStrict(dim, x, y, z)
    if not isinstance(m, RFRepeaterPlant):
        return
    orig = m.bdata[NodeData.K_MODES] or 0b0000
    if new_modes is not None:
        m.bdata[NodeData.K_MODES] = new_modes
        modes = new_modes
    elif single_dir is not None and single_mode is not None:
        m.bdata[NodeData.K_MODES] = modes = orig & ((1 << single_dir) ^ 0b1111) | (
            (1 << single_dir) if single_mode else 0
        )
    else:
        raise ValueError("new_modes or single_dir and single_mode must be specified")
    network_uuid = m.bdata[NodeData.K_BOUND_NETWORK_UUID]
    if network_uuid is None:
        logger.error(
            "RFRepeaterPlant: empty network uuid from blockactor@{}".format((x, y, z))
        )
        return
    networks_data = get_networks_data()
    nodes_data = get_nodes_data()
    network = get_network(network_uuid, networks_data)
    if network is None:
        logger.error("RFRepeaterPlant: Network not found at {}".format((x, y, z)))
        return
    node = get_node(dim, (x, y, z), nodes_data)
    if node is None:
        logger.error("RFRepeaterPlant: Node not found at {}".format((x, y, z)))
        return
    network.nodes[(x, y, z)] = modes
    node.modes = modes
    network.save_to_global_dict(networks_data)
    node.save_to_global_dict(nodes_data)
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    s = sum_network_data(network_uuid)
    east, west, south, north = unpack_modes(m.bdata[NodeData.K_MODES])
    RFRepeaterPlantSettingsUpdate(
        dim,
        x,
        y,
        z,
        node.bound_network_uuid[-6:],
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


def remove_node_and_flush(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    nodes_data = get_nodes_data()
    node_data = nodes_data.pop((dim,) + pos, None)
    if node_data is None:
        return
    node = NodeData(dim, pos, node_data)
    nuuid = node.bound_network_uuid
    networks_data = get_networks_data()
    _delete_network(networks_data, nuuid)
    nodes_inited = set()
    connected_nodes = node.connected_nodes
    for node_pos in connected_nodes:
        _remove_connected_node(dim, node_pos, pos, nodes_data)
        _init_network_from_one_node(
            dim, node_pos, networks_data, nodes_data, nodes_inited
        )
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)


def _init_network_from_one_node(
    dim,  # type: int
    pos,  # type: tuple[int, int, int]
    networks_data,  # type: dict[str, dict]
    nodes_data,  # type: dict[tuple[int, int, int, int], dict]
    nodes_inited=None,  # type: set[tuple[int, int, int]] | None
):
    if nodes_inited is None:
        nodes_inited = set()
    if pos in nodes_inited:
        return
    network = NetworkData.new(dim)
    _dfs_init_network(dim, pos, nodes_data, network, nodes_inited)
    network.save_to_global_dict(networks_data)
    for node_pos in nodes_inited:
        plant = GetMachineStrict(dim, *node_pos)
        if isinstance(plant, RFRepeaterPlant):
            plant.flush_data(network)


def _dfs_init_network(
    dim,  # type: int
    pos,  # type: tuple[int, int, int]
    nodes_data,  # type: dict[tuple[int, int, int, int], dict]
    network,  # type: NetworkData
    nodes_inited,  # type: set[tuple[int, int, int]]
):
    if pos in nodes_inited:
        return
    node = get_node(dim, pos, nodes_data)
    if node is None:
        return
    node.bound_network_uuid = network.uuid
    network.nodes[pos] = node.modes
    nodes_inited.add(pos)
    node.save_to_global_dict(nodes_data)
    for node_pos in node.connected_nodes:
        _dfs_init_network(dim, node_pos, nodes_data, network, nodes_inited)


def _add_node_to_network(dim, pos, network_uuid=None):
    # type: (int, tuple[int, int, int], str | None) -> str
    networks_data = get_networks_data()
    nodes_data = get_nodes_data()
    if network_uuid is None:
        network = NetworkData.new(dim)
        network_uuid = network.uuid
    else:
        network = get_network(network_uuid, networks_data)
        if network is None:
            raise ValueError("Network not found")
    network.add_node(pos, 0b0000)
    network.save_to_global_dict(networks_data)
    NodeData.new(dim, pos, network_uuid).save_to_global_dict(nodes_data)
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    plant = GetMachineStrict(dim, *pos)
    if isinstance(plant, RFRepeaterPlant):
        plant.flush_data(network)
    return network_uuid


def _remove_connected_node(dim, pos1, pos2, nodes_data):
    # type: (int, tuple[int, int, int], tuple[int, int, int], dict[tuple[int, int, int, int], dict]) -> None
    node1 = get_node(dim, pos1, nodes_data)
    node2 = get_node(dim, pos2, nodes_data)
    if node1 is not None:
        node1.disconnect_to_node(pos2)
        node1.save_to_global_dict(nodes_data)
    if node2 is not None:
        node2.disconnect_to_node(pos1)
        node2.save_to_global_dict(nodes_data)


def _delete_network(network_datas, network_uuid):
    # type: (dict[str, dict], str) -> None
    network_datas.pop(network_uuid, None)
