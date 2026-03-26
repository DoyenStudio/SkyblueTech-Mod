# coding=utf-8
import uuid
from mod.server.extraServerApi import GetLevelId
from mod_log import logger
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockEntityData,
    GetExtraData,
    SetExtraData,
)
from ....common.define.facing import OPPOSITE_FACING, FACING_DXYZ
from ....common.events.machinery.rf_repeater_plant import RFRepeaterPlantSettingsUpdate
from ....common.machinery_def.rf_repeater_plant import MODE_INPUT, MODE_OUTPUT
from ..pool import GetMachineStrict


K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"


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

    def add_node(self, node_pos, mode=0):
        # type: (tuple[int, int, int], int) -> None
        self.nodes[node_pos] = mode

    def remove_node(self, node_pos):
        # type: (tuple[int, int, int]) -> None
        self.nodes.pop(node_pos, None)

    def save_to_global_dict(self, network_datas):
        network_datas[self.uuid] = {
            self.K_DIM: self.dim,
            self.K_NODES: self.nodes,
        }


class NodeData(object):
    K_MODE = "mode"
    K_BOUND_NETWORK_UUID = "bound_nuuid"
    K_CONNECTED_NODES = "con_nodes"

    def __init__(self, dim, pos, node_data):
        # type: (int, tuple[int, int, int], dict) -> None
        self.dim = dim
        self.pos = pos
        self.bound_network_uuid = node_data[self.K_BOUND_NETWORK_UUID]  # type: str
        self.connected_nodes = node_data.get(self.K_CONNECTED_NODES, [])  # type: list[tuple[int, int, int]]
        self.mode = node_data.get(self.K_MODE, MODE_INPUT)

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
                cls.K_MODE: 0,
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
            self.K_MODE: self.mode,
            self.K_CONNECTED_NODES: self.connected_nodes,
        }
        # extra
        bdata = GetBlockEntityData(self.dim, (x, y, z))
        if bdata is None:
            logger.error("RFRepeaterPlant: Failed to dump: {}".format(self.pos))
            return
        bdata[self.K_CONNECTED_NODES] = [[x, y, z] for x, y, z in self.connected_nodes]
        bdata[self.K_BOUND_NETWORK_UUID] = self.bound_network_uuid
        bdata[self.K_MODE] = self.mode


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
            self.total_input_count += io_mode == MODE_INPUT
            self.total_output_count += io_mode == MODE_OUTPUT
            if isinstance(GetMachineStrict(network.dim, x, y, z), RFRepeaterPlant):
                self.network_plant_online_count += 1
                self.total_input_active_count += io_mode == MODE_INPUT
                self.total_output_active_count += io_mode == MODE_OUTPUT


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


def change_node_mode(dim, x, y, z, new_mode):
    # type: (int, int, int, int, int) -> None
    from ...transmitters.base.define import AP_MODE_INPUT, AP_MODE_OUTPUT
    from ...transmitters.wire.logic import logic_module
    from . import RFRepeaterPlant

    m = GetMachineStrict(dim, x, y, z)
    if not isinstance(m, RFRepeaterPlant):
        return
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
    network.nodes[(x, y, z)] = node.mode = bool(new_mode)
    network.save_to_global_dict(networks_data)
    node.save_to_global_dict(nodes_data)
    save_networks_data(networks_data)
    save_nodes_data(nodes_data)
    s = sum_network_data(network_uuid)
    io_mode = m.bdata[NodeData.K_MODE]
    RFRepeaterPlantSettingsUpdate(
        dim,
        x,
        y,
        z,
        node.bound_network_uuid[-6:],
        io_mode,
        s.network_plant_count,
        s.network_plant_online_count,
        s.total_output_count,
        s.total_output_active_count,
        s.total_input_count,
        s.total_input_active_count,
    ).sendMulti(m.sync.GetPlayersInSync())
    for face in (2, 3, 4, 5):
        dx, dy, dz = FACING_DXYZ[face]
        ap = logic_module.access_points_pool.get((
            dim,
            x + dx,
            y + dy,
            z + dz,
            OPPOSITE_FACING[face],
        ))
        if ap is None:
            continue
        res = logic_module.SetAccessPointIOMode(
            ap, [AP_MODE_INPUT, AP_MODE_OUTPUT][new_mode]
        )
        if not res:
            print("[Error] set node io mode failed")
    plant = GetMachineStrict(dim, *node.pos)
    if isinstance(plant, RFRepeaterPlant):
        plant.flush_data(network)


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
    network.nodes[pos] = node.mode
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
