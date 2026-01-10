# coding=utf-8
#
from collections import deque
from weakref import WeakValueDictionary as WValueDict
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    BlockHasTag,
    GetBlockTags,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.api.timer import Delay
from ...machinery.basic import BaseMachine
from ...machinery.pool import GetMachineStrict, GetMachineCls
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import FACING_EN, DXYZ_FACING
from .define import WireNetwork, WireAccessPoint, AP_MODE_INPUT, AP_MODE_OUTPUT
from .pool import WireNetworkPool, WireAccessPointPool, GNodes

# TYPE_CHECKING
if TYPE_CHECKING:
    PosData = tuple[int, int, int]  # x y z
# TYPE_CHECKING END

def isWire(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_wire")

def bothCanConnect(origName, blockName):
    # type: (str, str) -> bool
    tags = GetBlockTags(blockName)
    tags2 = GetBlockTags(origName)
    if "redstoneflux_connectable" not in tags or "redstoneflux_connectable" not in tags2:
        return False
    elif isWire(blockName) and isWire(blockName):
        return origName == blockName
    return True

def isRFMachine(blockName):
    return BlockHasTag(blockName, "redstoneflux_appliance") or BlockHasTag(
        blockName, "redstoneflux_generator"
    )

def isSkyblueMachine(block_tags):
    # type: (set[str]) -> bool
    return "skybluetech_machine" in block_tags

def isPowerProvider(block_tags, dim, posdata):
    # type: (set[str], int, tuple[int, int, int, int]) -> bool
    if isSkyblueMachine(block_tags):
        block_name = GetBlockName(dim, posdata[:3])
        if block_name is None:
            return False
        return GetMachineCls(block_name).energy_io_mode[posdata[3]] == 1
    return "redstoneflux_provider" in block_tags

def isPowerAccepter(block_tags, dim, posdata):
    # type: (set[str], int, tuple[int, int, int, int]) -> bool
    if isSkyblueMachine(block_tags):
        block_name = GetBlockName(dim, posdata[:3])
        if block_name is None:
            return False
        return GetMachineCls(block_name).energy_io_mode[posdata[3]] == 0
    return "redstoneflux_accepter" in block_tags

def bfsFindConnections(dim, start, connected=None):
    # type: (int, PosData, set[PosData] | None) -> WireNetwork | None
    # 确保 start 一定是线缆 !!!

    start_bname = GetBlockName(dim, start)
    if start_bname is None:
        return None
    if not isWire(start_bname):  # 确保 start 一定是线缆 !!!
        return None

    output_nodes = set()  # type: set[WireAccessPoint]
    input_nodes = set()  # type: set[WireAccessPoint]
    if connected is None:
        connected = set()
    nodes = set() # type: set[PosData]

    first_wire_name = None

    queue = deque([start])
    while queue:
        current = queue.popleft()
        cx, cy, cz = current

        _i = set()  # type: set[WireAccessPoint]
        _o = set()  # type: set[WireAccessPoint]
        for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            xyz = (cx + dx, cy + dy, cz + dz)
            if xyz in connected:
                continue
            gbname = GetBlockName(dim, xyz)
            if gbname is None:
                continue
            elif isWire(gbname):
                if not first_wire_name:
                    first_wire_name = gbname
                elif first_wire_name != gbname:
                    # 不同等级的线缆无法并用
                    continue
                queue.append(xyz)
                continue
            elif isRFMachine(gbname):
                block_tags = GetBlockTags(gbname)
                posdata = xyz + (OPPOSITE_FACING[facing],)
                if isPowerProvider(block_tags, dim, posdata):
                    _o.add(WireAccessPoint(dim, cx, cy, cz, facing, AP_MODE_OUTPUT))
                elif isPowerAccepter(block_tags, dim, posdata):
                    _i.add(WireAccessPoint(dim, cx, cy, cz, facing, AP_MODE_INPUT))
                else:
                    print("[ERROR] Machine wire con invalid: ", xyz, gbname)
                    continue
        input_nodes |= _i
        output_nodes |= _o
        connected.add(
            current
        )  # TODO: 线缆过多使得队列内存占用过大; 考虑限制最大 bfs 数
        nodes.add(current)

    return WireNetwork(
        dim,
        input_nodes,
        output_nodes,
        nodes,
        0,  # 目前无传输限制
    )

def getAndInitNetwork(dim, start, exists=None):
    # type: (int, PosData, set[PosData] | None) -> WireNetwork | None
    """
    在线缆位置获取并初始化传输网络。

    Args:
        dim (int): 维度 ID
        start (tuple[int, int, int]): 开始坐标
        exists (set, optional): 用于缓存路径点的set

    Returns:
        WireNetwork (optional): 传输网络
    """
    network = bfsFindConnections(dim, start, exists)
    if network is None:
        return None
    dim_datas = GNodes.setdefault(dim, WValueDict())
    for node in network.nodes:
        dim_datas[node] = network
    for ap in network.group_inputs | network.group_outputs:
        WireAccessPointPool[(network.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap
    return network

# def addContainerToNetwork(dim, x, y, z, network):
#     # type: (int, int, int, int, WireNetwork) -> None
#     """
#     初始化一个容器附近的所有传输网络。
#     一般是容器被创建时调用的。

#     Args:
#         dim (int): 维度 ID
#         x (int): x
#         y (int): y
#         z (int): z
#         network (WireNetwork): 传输网络
#     """


def clearNearbyNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    """
    清除一个容器附近的所有传输网络。
    一般是容器消失时调用的。

    Args:
        dim (int): 维度 ID
        x (int): x
        y (int): y
        z (int): z
    """
    WireNetworkPool.pop((dim, (x, y, z)), None)
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        opposite_facing = OPPOSITE_FACING[facing]
        ax, ay, az = x + dx, y + dy, z + dz
        ap = WireAccessPointPool.pop((dim, ax, ay, az, opposite_facing), None)
        if ap is not None:
            bound_network = ap.get_bounded_network()
            if bound_network is not None:
                bound_network.group_inputs.discard(ap)
                bound_network.group_outputs.discard(ap)
            else:
                print("[ERROR] Wire access point {} bound network None".format((dim, x, y, z, facing)))

def deleteNetwork(network):
    # type: (WireNetwork) -> None
    "完全清除一个网络。"
    for ap in network.group_inputs | network.group_outputs:
        WireAccessPointPool.pop((network.dim, ap.x, ap.y, ap.z, ap.access_facing), None)
        nws = WireNetworkPool.get((network.dim, ap.target_pos))
        if nws is None:
            continue
        i, o = nws
        if network in i:
            i.remove(network)
        elif network in o:
            o.remove(network)
        if not i and not o:
            WireNetworkPool.pop((network.dim, ap.target_pos))
    for node in network.nodes.copy():
        GNodes.get(network.dim, {}).pop(node, None)

def cleanAccessPointNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    """
    清理一个节点的网络数据。

    Args:
        dim (int): 维度 ID
        x (int): x
        y (int): y
        z (int): z
    """
    network = GNodes.get(dim, {}).pop((x, y, z), None) or GetNetworkByWire(dim, x, y, z)
    if network is not None:
        deleteNetwork(network)
    tmp_set = set()
    GetNetworkByWire(
        dim,
        x,
        y,
        z,
        tmp_set
    )
    GetNearbyWireNetworks(
        dim,
        x,
        y,
        z,
        tmp_set,
        enable_cache=False
    ) # 仅刷新

def cleanContainerNetworks(dim, x, y, z):
    # type: (int, int, int, int) -> None
    """
    清理一个容器周围的网络数据。

    Args:
        dim (int): 维度 ID
        x (int): x
        y (int): y
        z (int): z
    """
    i, o = GetNearbyWireNetworks(dim, x, y, z)
    for network in i + o:
        deleteNetwork(network)
    tmp_set = set()
    GetNetworkByWire(
        dim,
        x,
        y,
        z,
        tmp_set
    )
    GetNearbyWireNetworks(
        dim,
        x,
        y,
        z,
        tmp_set,
        enable_cache=False
    ) # 仅刷新


def GetNearbyWireNetworks(dim, x, y, z, exists=None, enable_cache=True):
    # type: (int, int, int, int, set[PosData] | None, bool) -> tuple[list[WireNetwork], list[WireNetwork]]
    """
    获取一个容器附近的输入和提取网络。

    Args:
        dim (int): 维度 ID
        x (int): 容器 x 坐标
        y (int): 容器 y 坐标
        z (int): 容器 z 坐标
        exists (set, optional): 路径缓存set
        enable_cache (bool, optional): 是否允许使用缓存

    Returns:
        tuple[set[WireNetwork], set[WireNetwork]]: 分别表示输入和提取模式的传输网络
    """
    if enable_cache:
        cached_network = WireNetworkPool.get((dim, (x, y, z)), None)
        if cached_network is not None:
            return cached_network
    input_networks = []  # type: list[WireNetwork]
    output_networks = []  # type: list[WireNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        network = getAndInitNetwork(dim, next_pos, _exists)
        if network is None:
            continue
        p = WireAccessPoint(dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1) # -1 表示输入输出模式未知
        if p in network.group_inputs:
            input_networks.append(network)
        elif p in network.group_outputs:
            output_networks.append(network)
    WireNetworkPool[(dim, (x, y, z))] = (input_networks, output_networks)
    return input_networks, output_networks

def GetNetworkByWire(dim, x, y, z, cacher=None):
    # type: (int, int, int, int, set[PosData] | None) -> WireNetwork | None
    network = GNodes.get(dim, {}).get((x, y, z))
    if network is not None:
        return network
    return getAndInitNetwork(dim, (x, y, z), cacher)

def RequireEnergyFromNetwork(machine):
    # type: (BaseMachine) -> bool
    ok = False
    networks = GetNearbyWireNetworks(machine.dim, machine.x, machine.y, machine.z)[0]
    for network in networks:
        if network is None:
            continue
        generator_nodes = network.get_output_access_points()
        for ap in generator_nodes:
            m2 = GetMachineStrict(machine.dim, *ap.target_pos)
            if m2 is None:
                continue
            m2.OnTryActivate() # 这样尝试输出能源
            ok = True
    return ok

@ServerPlaceBlockEntityEvent.Listen()
def onBlockPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if isWire(event.blockName):
        states = {}  # type: dict[str, bool]
        for dx, dy, dz in NEIGHBOR_BLOCKS_ENUM:
            facing_key = (
                "skybluetech:connection_" + FACING_EN[DXYZ_FACING[(dx, dy, dz)]]
            )
            bname = GetBlockName(
                event.dimension,
                (event.posX + dx, event.posY + dy, event.posZ + dz),
            )
            if bname is None:
                continue
            states[facing_key] = bothCanConnect(event.blockName, bname)
        UpdateBlockStates(event.dimension, (event.posX, event.posY, event.posZ), states)
        cleanAccessPointNetwork(event.dimension, event.posX, event.posY, event.posZ)
    elif isRFMachine(event.blockName):
        # 图方便
        cleanContainerNetworks(event.dimension, event.posX, event.posY, event.posZ)

@BlockRemoveServerEvent.Listen()
@Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if isRFMachine(event.fullName):
        clearNearbyNetwork(event.dimension, event.x, event.y, event.z)
    elif isWire(event.fullName):
        cleanAccessPointNetwork(event.dimension, event.x, event.y, event.z)

@BlockNeighborChangedServerEvent.Listen()
def onNeighbourBlockChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.fromBlockName == event.toBlockName:
        return
    if not isWire(event.blockName):
        return
    orig_can_connect = bothCanConnect(event.blockName, event.fromBlockName)
    can_connect = bothCanConnect(event.blockName, event.toBlockName)
    if orig_can_connect != can_connect:
        dxyz = (
            event.neighborPosX - event.posX,
            event.neighborPosY - event.posY,
            event.neighborPosZ - event.posZ,
        )
        facing_key = "skybluetech:connection_" + FACING_EN[DXYZ_FACING[dxyz]]
        UpdateBlockStates(
            event.dimensionId,
            (event.posX, event.posY, event.posZ),
            {facing_key: can_connect},
        )
