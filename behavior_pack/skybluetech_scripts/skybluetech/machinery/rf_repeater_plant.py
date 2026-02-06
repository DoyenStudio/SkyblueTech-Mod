# coding=utf-8
import uuid
from mod.server.blockEntityData import BlockEntityData
from mod.server.extraServerApi import GetLevelId
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockEntityData,
    CleanExtraData,
    GetExtraData,
    SetExtraData,
)
from ..define import flags
from ..define.id_enum.machinery import RF_REPEATER_PLANT as MACHINE_ID
from ..machinery_def.battery_cube import *
from .basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from .pool import GetMachineStrict

K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"
K_GLOBAL_BOUND_NETWORK_UUID = "bound_nuuid"
K_GLOBAL_NETWORK_DIM = "dim"
K_GLOBAL_NETWORK_NODES = "nodes"
K_GLOBAL_TRANSPORT_TYPE = "tt"
K_MODE = "mode"
K_BOUND_NETWORK_UUID = "bound_network_uuid"
K_CONNECT_NODES = "con_nodes"

MODE_SENDER = 0b01
MODE_RECEIVER = 0b10


@RegisterMachine
class RFRepeaterPlant(BaseMachine, GUIControl, ItemContainer):
    block_name = MACHINE_ID
    store_rf_max = 100000
    energy_io_mode = (1, 1, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)

    def OnPlaced(self, event):
        add_single_node(self.dim, self.x, self.y, self.z)

    def OnDestroy(self, event):
        remove_node_and_flush(self.dim, self.x, self.y, self.z)


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


def get_node_bound_network(dim, x, y, z):
    # type: (int, int, int, int) -> str | None
    res = get_nodes_data().get((dim, x, y, z))
    if res is None:
        return None
    return res[K_BOUND_NETWORK_UUID]


def get_nodes_in_network(network_uuid):
    # type: (str) -> list[tuple[tuple[int, int, int], int]]
    network_data = get_networks_data().get(network_uuid)
    if not network_data:
        return []
    return network_data[K_GLOBAL_NETWORK_NODES]


def add_single_node(dim, x, y, z):
    # type: (int, int, int, int) -> None
    networks_data = get_networks_data()
    _, nuuid = new_network(networks_data, dim)
    _add_node_to_network(dim, x, y, z, nuuid)
    save_networks_data(networks_data)


def build_connection(
    dim, # type: int
    node, # type: tuple[int, int, int]
    node2, # type: tuple[int, int, int]
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
    return True


def change_node_mode(dim, x, y, z, new_mode):
    # type: (int, int, int, int, int) -> None
    bdata = GetBlockEntityData(dim, x, y, z)
    if bdata is None:
        return
    bdata[K_MODE] = new_mode
    network_uuid = bdata[K_BOUND_NETWORK_UUID]
    if network_uuid is None:
        return
    networks_data = get_networks_data()
    network_data = networks_data.get(network_uuid)
    if network_data is None:
        print("[Error] RFRepeaterPlant: Network not found at {}".format((x, y, z)))
        return
    network_data[K_GLOBAL_NETWORK_NODES][(x, y, z)] = new_mode
    save_networks_data(networks_data)


def remove_node_and_flush(dim, x, y, z):
    # type: (int, int, int, int) -> None
    nodes_data = get_nodes_data()
    node_data = nodes_data.get((dim, x, y, z))
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
        reinit_network_from_one_node(dim, x, y, z, networks_data, nodes_data, nodes_inited)
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
    network_data[K_GLOBAL_NODES][(x, y, z)] = node_data
    near_nodes = node_data[K_CONNECT_NODES]  # type: list[tuple[int, int, int]]
    for node_x, node_y, node_z in near_nodes:
        _dfs_reinit_network(
            dim, node_x, node_y, node_z, nodes_data, nuuid, network_data, nodes_inited
        )

def _add_node_to_network(dim, x, y, z, network_uuid=None):
    # type: (int, int, int, int, str | None) -> None
    prev_networks = get_networks_data()
    if prev_networks is None:
        prev_networks = {}
    if network_uuid is None:
        network_data, network_uuid = new_network(prev_networks, dim)
    else:
        network_data = prev_networks[network_uuid]
    network_data[K_GLOBAL_NETWORK_NODES][(x, y, z)] = 0b00
    save_networks_data(prev_networks)

def _remove_connected_node(dim, x, y, z, nearby_node, nodes_data):
    # type: (int, int, int, int, tuple[int, int, int], dict[tuple[int, int, int, int], dict]) -> None
    node_data = nodes_data.get((dim, x, y, z))
    if node_data is None:
        return
    node_data[K_CONNECT_NODES].remove(nearby_node)

def new_network(networks_dict, dim):
    # type: (dict[str, dict], int) -> tuple[dict, str]
    nuuid = uuid.uuid4().hex
    networks_dict[nuuid] = {
        K_GLOBAL_NETWORK_DIM: dim,
        K_GLOBAL_NETWORK_NODES: {},
    }
    return networks_dict, nuuid


def new_node_data(dim, x, y, z, bound_network_uuid):
    # type: (int, int, int, int, str) -> dict
    return {
        K_GLOBAL_BOUND_NETWORK_UUID: bound_network_uuid,
        K_MODE: 0,
        K_CONNECT_NODES: [],
    }


def _pop_node_from_network(dim, x, y, z, network_datas, network_uuid):
    # type: (int, int, int, int, dict[str, dict], str) -> None
    network_data = network_datas.get(network_uuid)
    if network_data is None:
        return
    del network_data[K_GLOBAL_NETWORK_NODES][(x, y, z)]
    if not network_data[K_GLOBAL_NETWORK_NODES]:
        del network_datas[network_uuid]
