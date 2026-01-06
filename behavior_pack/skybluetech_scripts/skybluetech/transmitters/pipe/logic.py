# coding=utf-8
#
from collections import deque
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    ServerBlockUseEvent,
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
from skybluetech_scripts.tooldelta.api.server.tips import SetOnePopupNotice
from ...machinery.basic.fluid_container import FluidContainer
from ...machinery.basic.multi_fluid_container import MultiFluidContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import FACING_EN, FACING_ZHCN, DXYZ_FACING
from .define import PipeNetwork, PipeAccessPoint, AP_MODE_INPUT, AP_MODE_OUTPUT
from .pool import tankNetworkPool, tankAccessPointPool, GetSameNetwork

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
            dir_name = FACING_EN[facing]
            if block_states["skybluetech:connection_" + dir_name]:
                if block_states["skybluetech:cable_io_" + dir_name]:
                    _o.add(PipeAccessPoint(dim, cx, cy, cz, facing, AP_MODE_OUTPUT))
                else:
                    _i.add(PipeAccessPoint(dim, cx, cy, cz, facing, AP_MODE_INPUT))

        input_nodes |= _i
        output_nodes |= _o
        connected.add(
            current
        )  # TODO: 管道过多使得队列内存占用过大; 考虑限制最大 bfs 数

    return PipeNetwork(
        dim,
        input_nodes,
        output_nodes,
        0,  # 目前无传输限制
    )


def getNearbyPipeNetwork(dim, x, y, z, exists=None, enable_cache=False):
    # type: (int, int, int, int, set[PosData] | None, bool) -> tuple[set[PipeNetwork], set[PipeNetwork]]
    if enable_cache and (dim, x, y, z) in tankNetworkPool:
        return tankNetworkPool[(dim, (x, y, z))]
    input_networks = set()  # type: set[PipeNetwork]
    output_networks = set()  # type: set[PipeNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        network = bfsFindConnections(dim, next_pos, _exists)
        if network is None:
            continue
        p = PipeAccessPoint(dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1) # -1 表示输入输出模式未知
        if p in network.group_inputs:
            input_networks.add(GetSameNetwork(network))
        elif p in network.group_outputs:
            output_networks.add(GetSameNetwork(network))
    return input_networks, output_networks

def GetNetworkByCable(dim, x, y, z, cacher=None):
    # type: (int, int, int, int, set[PosData] | None) -> PipeNetwork | None
    network = bfsFindConnections(dim, (x, y, z), cacher)
    if network is not None:
        UploadNetworkToPool(network)
    return network

def GetTankNetworks(dim, x, y, z, enable_cache=False, cacher=None):
    # type: (int, int, int, int, bool, set[PosData] | None) -> tuple[set[PipeNetwork], set[PipeNetwork]]
    """
    获取某一位置(建议为流体容器)附近的管道网络。如果会使用缓存。

    Args:
        dim (int): 维度 id
        x (int): x
        y (int): y
        z (int): z
        enable_cache (bool, optional): 是否允许使用已缓存网络
        cacher (set, optional): 不使用已缓存网络的情况下, 用于 bfs 路径缓存的 set

    Returns:
        tuple: 对该流体容器进行(输入/提取)的所有管道网络
    """
    nws = tankNetworkPool.get((dim, (x, y, z)))
    if nws is not None:
        return nws
    i, o = getNearbyPipeNetwork(dim, x, y, z, enable_cache=enable_cache, exists=cacher)
    tankNetworkPool[(dim, (x, y, z))] = nws = (i, o)
    for network in i | o:
        UploadNetworkToPool(network)
    return nws


def clearNearbyPipesNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    "清除管道目标池数据"
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        ax, ay, az = x + dx, y + dy, z + dz
        tankNetworkPool.pop((dim, (ax, ay, az)), None)

def UploadNetworkToPool(network):
    # type: (PipeNetwork) -> None
    for ap in network.group_inputs:
        tankNetworkPool.setdefault((network.dim, (ap.x, ap.y, ap.z)), (set(), set()))[0].add(network)
    for ap in network.group_outputs:
        tankNetworkPool.setdefault((network.dim, (ap.x, ap.y, ap.z)), (set(), set()))[1].add(network)
    UpdateNetworkAccessPoints(network)

def UpdateNetworkAccessPoints(network):
    # type: (PipeNetwork) -> None
    for ap in network.group_inputs | network.group_outputs:
        tankAccessPointPool[(network.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap

def PostFluidIntoNetworks(dim, xyz, fluid_id, fluid_volume, networks, depth):
    # type: (int, tuple[int, int, int], str, float, set[PipeNetwork] | None, int) -> float
    "向网络发送流体, 返回剩余流体体积"
    if networks is None:
        x, y, z = xyz
        networks = GetTankNetworks(dim, x, y, z, enable_cache=True)[1]
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
    networks = GetTankNetworks(dim, x, y, z, enable_cache=True)[0]
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
    if BlockHasTag(event.blockName, "skybluetech_pipe"):
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


@BlockRemoveServerEvent.Listen()
@Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    m = GetMachineStrict(event.dimension, event.x, event.y, event.z)
    if m is not None:
        tankNetworkPool.pop((event.dimension, (event.x, event.y, event.z)), None)

@BlockNeighborChangedServerEvent.Listen()
def onNeighbourBlockChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.fromBlockName == event.toBlockName:
        return
    if not isPipe(event.blockName):
        return
    import time
    t = time.time()
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
    if canConnect(event.fromBlockName) or canConnect(event.toBlockName):
        clearNearbyPipesNetwork(event.dimensionId, event.neighborPosX, event.neighborPosY, event.neighborPosZ)
    if canConnect(event.toBlockName):
        GetTankNetworks(
            event.dimensionId,
            event.neighborPosX,
            event.neighborPosY,
            event.neighborPosZ,
        ) # 仅刷新
