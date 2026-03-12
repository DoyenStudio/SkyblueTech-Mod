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
    GetBlockEntityData,
    GetPlayerDimensionId,
    GetExtraData,
    SetExtraData,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ....common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
    RFRepeaterPlantBuildAddWire,
    RFRepeaterPlantSettingsUpdate,
    RFRepeaterPlantSettingUpload,
)
from ..pool import GetMachineStrict
from .utils import hypot, unpack_modes


K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"


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
        bdata = GetBlockEntityData(self.dim, (x, y, z))
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
        from . import RFRepeaterPlant

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


@RFRepeaterPlantBuildRequest.Listen()
def onEstablishConn(event):
    # type: (RFRepeaterPlantBuildRequest) -> None
    from . import RFRepeaterPlant, block_sync

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
    from . import RFRepeaterPlant

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
    from . import RFRepeaterPlant

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
    from . import RFRepeaterPlant

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
    from . import RFRepeaterPlant

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
