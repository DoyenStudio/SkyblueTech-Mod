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
    GetBlockStates,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.api.timer import Delay
from ...machinery.basic.fluid_container import FluidContainer
from ...machinery.basic.multi_fluid_container import MultiFluidContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import FACING_EN, DXYZ_FACING
from .define import PipeNetwork, PipeAccessPoint, AP_MODE_INPUT, AP_MODE_OUTPUT
from .pool import PipeNetworkPool, PipeAccessPointPool, GNodes

# TYPE_CHECKING
if TYPE_CHECKING:
    PosData = tuple[int, int, int]  # x y z
# TYPE_CHECKING END

PIPE_NAME = "skybluetech:bronze_pipe"


def isPipe(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_pipe")

def canConnect(blockName):
    # type: (str) -> bool
    return blockName == PIPE_NAME or BlockHasTag(
        blockName, "skybluetech_fluid_container"
    )

def isFluidContainer(blockName):
    return BlockHasTag(blockName, "skybluetech_fluid_container")

def bfsFindConnections(dim, start, connected=None):
    # type: (int, PosData, set[PosData] | None) -> PipeNetwork | None
    # 确保 start 一定是管道 !!!

    start_bname = GetBlockName(dim, start)
    if start_bname is None:
        return None
    if not isPipe(start_bname):  # 确保 start 一定是管道 !!!
        return None

    output_nodes = set()  # type: set[PipeAccessPoint]
    input_nodes = set()  # type: set[PipeAccessPoint]
    if connected is None:
        connected = set()
    nodes = set() # type: set[PosData]

    first_cable_name = None

    queue = deque([start])
    while queue:
        current = queue.popleft()
        cx, cy, cz = current
        block_states = GetBlockStates(dim, current)

        _i = set()  # type: set[PipeAccessPoint]
        _o = set()  # type: set[PipeAccessPoint]
        for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            xyz = (cx + dx, cy + dy, cz + dz)
            if xyz in connected:
                continue
            gbname = GetBlockName(dim, xyz)
            if gbname is None:
                continue
            elif isPipe(gbname):
                queue.append(xyz)
                if not first_cable_name:
                    first_cable_name = gbname
                # elif first_cable_name != gbname:
                #     # 不同等级的管道无法并用
                #     continue
                continue
            elif isFluidContainer(gbname):
                dir_name = FACING_EN[facing]
                if block_states["skybluetech:cable_io_" + dir_name]:
                    _o.add(PipeAccessPoint(dim, cx, cy, cz, facing, AP_MODE_OUTPUT))
                else:
                    _i.add(PipeAccessPoint(dim, cx, cy, cz, facing, AP_MODE_INPUT))
        input_nodes |= _i
        output_nodes |= _o
        connected.add(
            current
        )  # TODO: 管道过多使得队列内存占用过大; 考虑限制最大 bfs 数
        nodes.add(current)

    return PipeNetwork(
        dim,
        input_nodes,
        output_nodes,
        nodes,
        0,  # 目前无传输限制
    )

def getAndInitNetwork(dim, start, exists=None):
    # type: (int, PosData, set[PosData] | None) -> PipeNetwork | None
    """
    在管道位置获取并初始化传输网络。

    Args:
        dim (int): 维度 ID
        start (tuple[int, int, int]): 开始坐标
        exists (set, optional): 用于缓存路径点的set

    Returns:
        PipeNetwork (optional): 传输网络
    """
    network = bfsFindConnections(dim, start, exists)
    if network is None:
        return None
    dim_datas = GNodes.setdefault(dim, WValueDict())
    for node in network.nodes:
        dim_datas[node] = network
    for ap in network.group_inputs | network.group_outputs:
        PipeAccessPointPool[(network.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap
        PipeNetworkPool.setdefault(
            (network.dim, ap.target_pos),
            (set(), set())
        )[ap.io_mode].add(network)
    return network

# def addContainerToNetwork(dim, x, y, z, network):
#     # type: (int, int, int, int, PipeNetwork) -> None
#     """
#     初始化一个容器附近的所有传输网络。
#     一般是容器被创建时调用的。

#     Args:
#         dim (int): 维度 ID
#         x (int): x
#         y (int): y
#         z (int): z
#         network (PipeNetwork): 传输网络
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
    PipeNetworkPool.pop((dim, (x, y, z)), None)
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        opposite_facing = OPPOSITE_FACING[facing]
        ax, ay, az = x + dx, y + dy, z + dz
        ap = PipeAccessPointPool.pop((dim, ax, ay, az, opposite_facing), None)
        if ap is not None:
            bound_network = ap.get_bounded_network()
            if bound_network is not None:
                bound_network.group_inputs.discard(ap)
                bound_network.group_outputs.discard(ap)
            else:
                print("[ERROR] Pipe access point {} bound network None".format((dim, x, y, z, facing)))

def deleteNetwork(network):
    # type: (PipeNetwork) -> None
    "完全清除一个网络。"
    for io in network.group_inputs | network.group_outputs:
        PipeAccessPointPool.pop((network.dim, io.x, io.y, io.z, io.access_facing), None)
        PipeNetworkPool.pop((network.dim, io.target_pos), None)
        for node in network.nodes:
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
    network = GNodes.get(dim, {}).pop((x, y, z), None) or GetNetworkByPipe(dim, x, y, z)
    if network is not None:
        deleteNetwork(network)
    tmp_set = set()
    GetNearbyPipeNetworks(
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
    i, o = GetNearbyPipeNetworks(dim, x, y, z)
    for network in i | o:
        deleteNetwork(network)
    tmp_set = set()
    GetNearbyPipeNetworks(
        dim,
        x,
        y,
        z,
        tmp_set,
        enable_cache=False
    ) # 仅刷新


def GetNearbyPipeNetworks(dim, x, y, z, exists=None, enable_cache=True):
    # type: (int, int, int, int, set[PosData] | None, bool) -> tuple[set[PipeNetwork], set[PipeNetwork]]
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
        tuple[set[PipeNetwork], set[PipeNetwork]]: 分别表示输入和提取模式的传输网络
    """
    if enable_cache:
        cached_network = PipeNetworkPool.get((dim, (x, y, z)), None)
        if cached_network is not None:
            return cached_network
    input_networks = set()  # type: set[PipeNetwork]
    output_networks = set()  # type: set[PipeNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        network = getAndInitNetwork(dim, next_pos, _exists)
        if network is None:
            continue
        p = PipeAccessPoint(dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1) # -1 表示输入输出模式未知
        if p in network.group_inputs:
            input_networks.add(network)
        elif p in network.group_outputs:
            output_networks.add(network)
    return input_networks, output_networks

def GetNetworkByPipe(dim, x, y, z, cacher=None):
    # type: (int, int, int, int, set[PosData] | None) -> PipeNetwork | None
    network = GNodes.get(dim, {}).get((x, y, z))
    if network is not None:
        return network
    return getAndInitNetwork(dim, (x, y, z), cacher)

def PostFluidIntoNetworks(dim, xyz, fluid_id, fluid_volume, networks, depth):
    # type: (int, tuple[int, int, int], str, float, set[PipeNetwork] | None, int) -> float
    "向网络发送流体, 返回剩余流体体积"
    if networks is None:
        x, y, z = xyz
        networks = GetNearbyPipeNetworks(dim, x, y, z, enable_cache=True)[1]
    for ap in sorted(
        list(i for network in networks for i in network.group_inputs),
        key=lambda ap: ap.get_priority(),
        reverse=True,
    ):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[ap.access_facing]
        cxyz = (ap.x + dx, ap.y + dy, ap.z + dz)
        if xyz == cxyz:
            # 别自己给自己装东西 !
            continue
        m = GetMachineWithoutCls(dim, ap.x + dx, ap.y + dy, ap.z + dz)
        if m is None:
            continue
            # 目前不处理任何非流体容器方块
        if not isinstance(m, (FluidContainer, MultiFluidContainer)):
            raise ValueError("Machine %s is not a FluidContainer" % type(m).__name__)
        _, fluid_volume = m.AddFluid(fluid_id, fluid_volume, depth=depth+1)
        if fluid_volume <= 0:
            break
    return fluid_volume

def RequirePostFluid(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    "网络内某个节点向网络请求流体。"
    x, y, z = xyz
    networks = GetNearbyPipeNetworks(dim, x, y, z, enable_cache=True)[0]
    for ap in sorted(
        list(i for network in networks for i in network.group_outputs),
        key=lambda ap: ap.get_priority(),
        reverse=True,
    ):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[ap.access_facing]
        cxyz = (ap.x + dx, ap.y + dy, ap.z + dz)
        if xyz == cxyz:
            # 别自己给自己提取 !
            continue
        m = GetMachineWithoutCls(dim, ap.x + dx, ap.y + dy, ap.z + dz)
        if isinstance(m, (FluidContainer, MultiFluidContainer)):
            m.RequirePost()

@ServerPlaceBlockEntityEvent.Listen()
def onBlockPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if isPipe(event.blockName):
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
            states[facing_key] = canConnect(bname)
        UpdateBlockStates(event.dimension, (event.posX, event.posY, event.posZ), states)
        cleanAccessPointNetwork(event.dimension, event.posX, event.posY, event.posZ)
    elif isFluidContainer(event.blockName):
        # 图方便
        print("Exec")
        cleanContainerNetworks(event.dimension, event.posX, event.posY, event.posZ)

@BlockRemoveServerEvent.Listen()
@Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if isFluidContainer(event.fullName):
        clearNearbyNetwork(event.dimension, event.x, event.y, event.z)
    elif isPipe(event.fullName):
        cleanAccessPointNetwork(event.dimension, event.x, event.y, event.z)

@BlockNeighborChangedServerEvent.Listen()
def onNeighbourBlockChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.fromBlockName == event.toBlockName:
        return
    if not isPipe(event.blockName):
        return
    from_block_can_connect = canConnect(event.fromBlockName)
    to_block_can_connect = canConnect(event.toBlockName)
    if from_block_can_connect != to_block_can_connect:
        dxyz = (
            event.neighborPosX - event.posX,
            event.neighborPosY - event.posY,
            event.neighborPosZ - event.posZ,
        )
        facing_key = "skybluetech:connection_" + FACING_EN[DXYZ_FACING[dxyz]]
        if isPipe(event.toBlockName):
            io_key = "skybluetech:cable_io_" + FACING_EN[DXYZ_FACING[dxyz]]
            UpdateBlockStates(
                event.dimensionId,
                (event.posX, event.posY, event.posZ),
                {facing_key: to_block_can_connect, io_key: False},
            )
        else:
            UpdateBlockStates(
                event.dimensionId,
                (event.posX, event.posY, event.posZ),
                {facing_key: to_block_can_connect},
            )
