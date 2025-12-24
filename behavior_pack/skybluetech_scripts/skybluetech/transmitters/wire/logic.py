# coding=utf-8
#
from collections import deque
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    GetBlockTags,
    BlockHasTag,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.api.timer import Delay, ExecLater
from ...machinery.pool import GetMachineWithoutCls, GetMachineStrict, GetMachineCls, cached_machines
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import FACING_EN, DXYZ_FACING
from .define import WireNetwork, WireLevelEnum
from .pool import GetSameNetwork, GetCachedNetworkFromPos, SetNetworkToPos

# TYPE_CHECKING
if TYPE_CHECKING:
    from ...machinery.basic.base_machine import BaseMachine
    PosData = tuple[int, int, int, int] # x y z facing
# TYPE_CHECKING END

def canConnect(origName, blockName):
    # type: (str, str) -> bool
    tags = GetBlockTags(blockName)
    tags2 = GetBlockTags(origName)
    if "redstoneflux_connectable" not in tags:
        return False
    elif isWire(tags) and isWire(tags2):
        return origName == blockName
    return True

def isWire(block_tags):
    # type: (set[str]) -> bool
    return "skybluetech_wire" in block_tags

def isMachine(block_tags):
    # type: (set[str]) -> bool
    return "redstoneflux_machine" in block_tags or isSkyblueMachine(block_tags)

def isSkyblueMachine(block_tags):
    # type: (set[str]) -> bool
    return "skybluetech_machine" in block_tags

def isPowerProvider(block_tags, dim, posdata):
    # type: (set[str], int, PosData) -> bool
    if isSkyblueMachine(block_tags):
        block_name = GetBlockName(dim, posdata[:3])
        if block_name is None:
            return False
        return GetMachineCls(block_name).energy_io_mode[posdata[3]] == 1
    return "redstoneflux_provider" in block_tags

def isPowerAccepter(block_tags, dim, posdata):
    # type: (set[str], int, PosData) -> bool
    if isSkyblueMachine(block_tags):
        block_name = GetBlockName(dim, posdata[:3])
        if block_name is None:
            return False
        return GetMachineCls(block_name).energy_io_mode[posdata[3]] == 0
    return "redstoneflux_accepter" in block_tags

def bfsFindConnections(dim, start, connected=None):
    # type: (int, PosData, set[PosData] | None) -> WireNetwork | None
    "start 只能是线缆！"
    power_provider_nodes = set() # type: set[PosData] # PosData = tuple[int, int, int, int] 最后一个 int 表示机器是通过哪个面接入网络的
    power_accepter_nodes = set() # type: set[PosData]
    if connected is None:
        connected = set()

    start = start[:3] + (OPPOSITE_FACING[start[3]],) # 这里 facing 指的是 bfs 搜索前进方向
    # # pre-process
    if start in connected: # 防止六面重复判断接线
        return None
    bname = GetBlockName(dim, start[:3])
    if bname is None:
        return None
    btags = GetBlockTags(bname)
    if not isWire(btags): # 不是线缆
        raise ValueError("Start is not a wire")
    first_wire_name = bname
    # # pre-process end

    queue = deque([start])
    w = WireNetwork(dim, set(), set(), 0)
    while queue:
        current = queue.popleft()
        connected.add(current) # TODO: 线缆过多使得队列内存占用过大; 考虑限制最大 bfs 数
        cx, cy, cz, _ = current
        for next_facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            opposite_facing = OPPOSITE_FACING[next_facing]
            next_pos = (cx + dx, cy + dy, cz + dz, opposite_facing)
            if next_pos in connected:
                continue
            bname = GetBlockName(dim, next_pos[:3])
            if bname is None:
                continue
            btags = GetBlockTags(bname)
            if isPowerProvider(btags, dim, next_pos):
                power_provider_nodes.add(next_pos)
                SetNetworkToPos((dim,) + next_pos, w)
            elif isPowerAccepter(btags, dim, next_pos):
                power_accepter_nodes.add(next_pos)
                SetNetworkToPos((dim,) + next_pos, w)
            elif isWire(btags):
                if not first_wire_name:
                    first_wire_name = bname
                elif first_wire_name != bname:
                    # 不同等级的电缆无法并用
                    continue
                queue.append(next_pos)
                w.AddWireNode(next_pos[:3])
    if first_wire_name is None:
        raise ValueError("Invalid wire network")
    w.group_appliances = power_accepter_nodes
    w.group_generators = power_provider_nodes
    w.wire_level = WireLevelEnum.from_block_name(first_wire_name)
    w.updateAllDevices()
    return w

def clearNearbyMachinesFacingNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        ax, ay, az = x + dx, y + dy, z + dz
        m = GetMachineWithoutCls(dim, ax, ay, az)
        if m is None or m.is_non_energy_machine:
            continue
        m.rf_networks[OPPOSITE_FACING[facing]] = None
        SetNetworkToPos((dim, ax, ay, az, OPPOSITE_FACING[facing]), None)

def clearMachineNetwork(dim, x, y, z, m=None):
    # type: (int, int, int, int, BaseMachine | None) -> None
    if m is None:
        m = GetMachineStrict(dim, x, y, z)
    if m is None:
        raise ValueError("Machine not found at (%d, %d, %d)" % (x, y, z))
    if m.is_non_energy_machine:
        return
    networks = m.rf_networks
    for facing, network in enumerate(networks):
        if network is not None:
            SetNetworkToPos((dim, x, y, z, facing), None)

# 可以从机器坐标开始找, 也可以从线缆坐标开始找
def GetNearbyWireNetwork(dim, x, y, z, exists=None):
    # type: (int, int, int, int, set[PosData] | None) -> list[WireNetwork | None]
    """
    获取一个方块邻近的网络信息。
    找到之后会同时更新整个网络。
    """
    networks = [None] * 6 # type: list[WireNetwork | None]
    _exists = exists or set() # type: set[PosData]
    start_bname = GetBlockName(dim, (x, y, z))
    if start_bname is None:
        return [] # never happens
    start_btags = GetBlockTags(start_bname)
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        # 在电缆初始化时会遇到一个电缆被它附近机器几次初始化的情况 这肯定是不行的
        # 所以需要缓存
        existing_network = GetCachedNetworkFromPos((dim, x, y, z, facing))
        # 如果是机器初始化的时候初始化网络
        # 那么肯定会在初始化的时候遍历到未初始化的机器
        # 这时候创建网络完成了之后就不能过快 CallWakeup, 需确认网络内所有机器都初始化完成之后才能 Call
        # 所以网络就有一个属性 inited_devices 和 all_devices
        # 但是这又诞生了一个新的问题: 如果这个机器是后放置的, 那么旧的网络也已缓存了, 就会使用旧的网络
        # 这样一来机器实际上调用的是旧的网络, 所以要一个判别方法 not AllDevicesInited()
        # 然后我们还需要把旧的网络全部更换成新的
        if existing_network is not None and not existing_network.AllDevicesInited():
            networks[facing] = existing_network
            continue
        start_fpos = (x, y, z, facing)
        current_fpos = (x + dx, y + dy, z + dz, facing)
        start_is_appliance = isPowerAccepter(start_btags, dim, start_fpos)
        start_is_generator = isPowerProvider(start_btags, dim, start_fpos)
        current_block = GetBlockName(dim, (x + dx, y + dy, z + dz))
        if current_block is None:
            continue
        current_block_tags = GetBlockTags(current_block)
        if isMachine(current_block_tags):
            # 二元网络
            current_opfpos = (x + dx, y + dy, z + dz, OPPOSITE_FACING[facing])
            if start_is_appliance and isPowerProvider(current_block_tags, dim, current_opfpos):
                network = WireNetwork(dim, {current_opfpos}, {start_fpos})
            elif start_is_generator and isPowerAccepter(current_block_tags, dim, current_opfpos):
                network = WireNetwork(dim, {start_fpos}, {current_opfpos})
            else:
                # 发电机和发电机 / 用电器和用电器连接在一起是无意义的网络
                continue
            SetNetworkToPos((dim, x, y, z, facing), network)
        elif isWire(current_block_tags):
            network = bfsFindConnections(dim, current_fpos, _exists)
            if network is None:
                continue
        else:
            continue
        network.updateAllDevices()
        networks[facing] = GetSameNetwork(network)
        UpdateWholeNetwork(dim, network)
    return networks

def UpdateWholeNetwork(dim, network):
    # type: (int, WireNetwork) -> None
    "更新整个网络, 先更新接入点面的信息再尝试激活机器。"
    for pos in network.GetAllPoses():
        x, y, z, facing = pos
        m = GetMachineStrict(dim, x, y, z)
        if m is None:
            continue
        m.rf_networks[facing] = network
        print "216:TryActivate", type(m).__name__
        m.OnTryActivate()

# 只有等到了整个网络内的机器全部初始化完了才可以唤醒网络
# 否则递归会超过递归最大深度

@Delay(0)
def CallNetworkWake(dim, network):
    # type: (int, WireNetwork) -> None
    # wakeUpWholeNetwork(dim, network)
    network.AddAwakeNum()
    if network.AllDevicesInited():
        wakeUpWholeNetwork(dim, network)

def wakeUpWholeNetwork(dim, network):
    # type: (int, WireNetwork) -> None
    "尝试激活网络中的每个接入点。"
    for pos in network.GetAllPoses():
        x, y, z, _ = pos
        m = GetMachineStrict(dim, x, y, z)
        if m is None:
            continue
        print "238:TryActivate", type(m).__name__
        m.OnTryActivate()
            

def RequireEnergyFromNetwork(machine):
    # type: (BaseMachine) -> bool
    ok = False
    for network in machine.rf_networks:
        if network is None:
            continue
        generator_nodes = network.group_generators
        for gx, gy, gz, _ in generator_nodes:
            m2 = GetMachineStrict(machine.dim, gx, gy, gz)
            if m2 is None:
                continue
            m2.OnTryActivate() # 这样尝试输出能源
            ok = True
    return ok
        

@ServerPlaceBlockEntityEvent.Listen()
def onBlockPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    # 机器放置就不判定了, 去机器初始化判定
    # if BlockHasTag(event.blockName, "skybluetech_machine"):
    #     # cacher 可以有效减少多面同线判断次数
    #     cacher = set() # type: set[PosData]
    #     for network in GetNearbyWireNetwork(event.dimension, event.posX, event.posY, event.posZ, cacher):
    #         UpdateWholeNetwork(event.dimension, network)
    if BlockHasTag(event.blockName, "skybluetech_wire"):
        network = bfsFindConnections(event.dimension, (event.posX, event.posY, event.posZ, 0))
        if network is not None:
            UpdateWholeNetwork(event.dimension, network)
        states = {} # type: dict[str, bool]
        for dx, dy, dz in NEIGHBOR_BLOCKS_ENUM:
            facing_key = "skybluetech:connection_" + FACING_EN[DXYZ_FACING[(dx, dy, dz)]]
            bname = GetBlockName(
                event.dimension,
                (event.posX + dx, event.posY + dy, event.posZ + dz),
            )
            if bname is None:
                continue
            states[facing_key] = canConnect(event.blockName, bname)
        UpdateBlockStates(event.dimension, (event.posX, event.posY, event.posZ), states)
            
@BlockRemoveServerEvent.Listen()
@Delay(0) # 等待下一 tick, 此时才能保证此处方块为空
def onWireRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if BlockHasTag(event.fullName, "skybluetech_wire"):
        if BlockHasTag(event.fullName, "skybluetech_machine"):
            clearMachineNetwork(event.dimension, event.x, event.y, event.z)
        clearNearbyMachinesFacingNetwork(event.dimension, event.x, event.y, event.z)
        # cacher 可以有效减少多面同线判断次数
        cacher = set() # type: set[PosData]
        for network in GetNearbyWireNetwork(event.dimension, event.x, event.y, event.z, cacher):
            if network is None:
                continue
            # UpdateWholeNetwork(event.dimension, network)

def PreRemoveMachine(event, machine):
    # type: (BlockRemoveServerEvent, BaseMachine) -> None
    clearMachineNetwork(event.dimension, event.x, event.y, event.z, machine)
    clearNearbyMachinesFacingNetwork(event.dimension, event.x, event.y, event.z)

@Delay(0)
def AfterRemoveMachine(event):
    # type: (BlockRemoveServerEvent) -> None
    # cacher 可以有效减少多面同线判断次数
    cacher = set() # type: set[PosData]
    for network in GetNearbyWireNetwork(event.dimension, event.x, event.y, event.z, cacher):
        if network is None:
            continue
        # UpdateWholeNetwork(event.dimension, network)

@BlockNeighborChangedServerEvent.Listen()
def onNeighbourBlockChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if isWire(GetBlockTags(event.blockName)):
        from_block_can_connect = canConnect(event.blockName, event.fromBlockName)
        to_block_can_connect = canConnect(event.blockName, event.toBlockName)
        if from_block_can_connect != to_block_can_connect:
            dxyz = (
                event.neighborPosX - event.posX,
                event.neighborPosY - event.posY,
                event.neighborPosZ - event.posZ
            )
            facing_key = "skybluetech:connection_" + FACING_EN[DXYZ_FACING[dxyz]]
            UpdateBlockStates(
                event.dimensionId,
                (event.posX, event.posY, event.posZ),
                {facing_key: to_block_can_connect}
            )
