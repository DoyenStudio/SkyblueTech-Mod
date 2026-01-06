# coding=utf-8
#
from collections import deque
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    ServerBlockUseEvent,
    BlockNeighborChangedServerEvent,
    ContainerItemChangedServerEvent,
    PushUIRequest,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    BlockHasTag,
    GetBlockStates,
    UpdateBlockStates,
    SetOnePopupNotice,
)
from skybluetech_scripts.tooldelta.api.server.container import (
    GetContainerItem,
    SetContainerItem,
    GetContainerSize,
)
from skybluetech_scripts.tooldelta.api.timer import Delay
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import COMMON_CONTAINERS, FACING_EN, DXYZ_FACING
from .define import CableNetwork, CableAccessPoint, AP_MODE_INPUT, AP_MODE_OUTPUT
from .pool import containerNetworkPool, containerAccessPointPool, GetSameNetwork

# TYPE_CHECKING
if 0:
    PosData = tuple[int, int, int]  # x y z
    PosDataWithFacing = tuple[int, int, int, int]  # x y z facing
# TYPE_CHECKING END

# 调节这个设置为 True 可以使管道一次性发送完所有物品
# 相应的, 性能可能将下降, 因为它会遍历容器内所有格子
POST_ALL_ITEMS_IN_ONE_TIME = False
ITEM_POST_DELAY = 0.2

# 输入型网络: 网络向此容器输入物品
# 输出型网络: 网络向此容器提取物品

# todo: 后续优化:
#       1. 添加物品过滤功能
#       2. 如果找到了可投递的容器, 下次优先向此容器进行投递, 提高命中率


def isCable(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_cable")


def canConnect(blockName):
    # type: (str) -> bool
    return (
        blockName in COMMON_CONTAINERS
        or blockName == "skybluetech:item_transport_cable"
        or BlockHasTag(blockName, "skybluetech_container")
    )

def isContainer(blockName):
    return blockName in COMMON_CONTAINERS or BlockHasTag(blockName, "skybluetech_container")

def bfsFindConnections(dim, start, connected=None):
    # type: (int, PosData, set[PosData] | None) -> CableNetwork | None
    # 从某一管道开始, 建立管道网络
    # 确保 start 一定是管道 !!!

    start_bname = GetBlockName(dim, start)
    if start_bname is None:
        return None
    if not isCable(start_bname):  # 确保 start 一定是管道 !!!
        return None

    output_nodes = set()  # type: set[CableAccessPoint]
    input_nodes = set()  # type: set[CableAccessPoint]
    if connected is None:
        connected = set()

    first_cable_name = None

    queue = deque([start])
    while queue:
        current = queue.popleft()
        cx, cy, cz = current
        block_states = GetBlockStates(dim, current)

        _i = set()  # type: set[CableAccessPoint]
        _o = set()  # type: set[CableAccessPoint]
        for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            xyz = (cx + dx, cy + dy, cz + dz)
            if xyz in connected:
                continue
            gbname = GetBlockName(dim, xyz)
            if gbname is None:
                continue
            elif isCable(gbname):
                queue.append(xyz)
                if not first_cable_name:
                    first_cable_name = gbname
                # elif first_cable_name != gbname:
                #     # 不同等级的管道无法并用
                #     continue
                continue
            elif isContainer(gbname):
                dir_name = FACING_EN[facing]
                if block_states["skybluetech:connection_" + dir_name]:
                    if block_states["skybluetech:cable_io_" + dir_name]:
                        _o.add(CableAccessPoint(dim, cx, cy, cz, facing, AP_MODE_OUTPUT))
                    else:
                        _i.add(CableAccessPoint(dim, cx, cy, cz, facing, AP_MODE_INPUT))

        input_nodes |= _i
        output_nodes |= _o
        connected.add(
            current
        )  # TODO: 管道过多使得队列内存占用过大; 考虑限制最大 bfs 数
    return CableNetwork(
        dim,
        input_nodes,
        output_nodes,
        0,  # 目前无传输限制
    )


def getNearbyCableNetwork(dim, x, y, z, exists=None, enable_cache=False):
    # type: (int, int, int, int, set[PosData] | None, bool) -> tuple[set[CableNetwork], set[CableNetwork]]
    if enable_cache and (dim, x, y, z) in containerNetworkPool:
        return containerNetworkPool[(dim, (x, y, z))]
    input_networks = set()  # type: set[CableNetwork]
    output_networks = set()  # type: set[CableNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        network = bfsFindConnections(dim, next_pos, _exists)
        if network is None:
            continue
        p = CableAccessPoint(dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1) # -1 表示输入输出模式未知
        if p in network.group_inputs:
            input_networks.add(GetSameNetwork(network))
        elif p in network.group_outputs:
            output_networks.add(GetSameNetwork(network))
    return input_networks, output_networks

def GetNetworkByCable(dim, x, y, z, cacher=None):
    # type: (int, int, int, int, set[PosData] | None) -> CableNetwork | None
    network = bfsFindConnections(dim, (x, y, z), cacher)
    if network is not None:
        UploadNetworkToPool(network)
    return network

def GetContainerNetworks(dim, x, y, z, enable_cache=False, cacher=None):
    # type: (int, int, int, int, bool, set[PosData] | None) -> tuple[set[CableNetwork], set[CableNetwork]]
    """
    返回某一个坐标的容器周围的网络，返回分别为输入型和提取型网络。
    如果要调用多次, 可先创建一个空集合, exists 参数传入这个集合, 以便 bfs 复用。
    enable_cache=True 时, 会优先从管道网络缓存里获取管道网络, 而非重新 bfs。
    """
    if enable_cache:
        nws = containerNetworkPool.get((dim, (x, y, z)))
        if nws is not None:
            return nws
    i, o = getNearbyCableNetwork(dim, x, y, z, exists=cacher)
    containerNetworkPool[(dim, (x, y, z))] = nws = (i, o)
    for network in i | o:
        UploadNetworkToPool(network)
    return nws

def PostItemIntoNetworks(dim, xyz, item, networks):
    # type: (int, tuple[int, int, int], Item, set[CableNetwork] | None) -> None | Item
    "向网络发送物品, 返回剩余物品"
    if networks is None:
        x, y, z = xyz
        networks = GetContainerNetworks(dim, x, y, z, enable_cache=True)[1]
    stack_size = item.GetBasicInfo().maxStackSize
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
        if m is not None:
            # 是机器
            if not isinstance(m, ItemContainer):
                raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
            available_slots = m.input_slots
        else:
            container_size = GetContainerSize(cxyz, dim)
            if container_size is None:
                continue
            available_slots = range(container_size)
        for slot in available_slots:
            sitem = GetContainerItem(dim, cxyz, slot, getUserData=True)
            if sitem is None:
                if m is not None and not m.IsValidInput(slot, item):
                    continue
                res = SetContainerItem(dim, cxyz, slot, item)
                if res:
                    return None
                else:
                    continue
            elif not sitem.CanMerge(item):
                continue
            final_count = min(sitem.count + item.count, stack_size)
            count_overflow = max(0, sitem.count + item.count - stack_size)
            sitem.count = final_count
            if count_overflow < stack_size:
                res = SetContainerItem(dim, cxyz, slot, sitem)
                if not res:
                    continue
                if count_overflow == 0:
                    return None
                else:
                    item.count = count_overflow
    return item


def RequireItems(dim, xyz):
    # type: (int, tuple[int, int, int]) -> bool
    "在某一个坐标的容器向周围的网络请求物品。"
    x, y, z = xyz
    networks = GetContainerNetworks(dim, x, y, z, enable_cache=True)[0]
    om = GetMachineStrict(dim, x, y, z)
    ok = False
    if om is None:
        myslots = range(GetContainerSize(xyz, dim))
    elif not isinstance(om, ItemContainer):
        raise ValueError("Machine %s is not a ItemContainer" % type(om).__name__)
    else:
        myslots = om.input_slots
    for ap in sorted(
        list(i for network in networks for i in network.group_outputs),
        key=lambda ap: ap.get_priority(),
    ):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[ap.access_facing]
        cxyz = (ap.x + dx, ap.y + dy, ap.z + dz)
        if xyz == cxyz:
            # 别自己给自己提取 !
            continue
        m = GetMachineWithoutCls(dim, ap.x + dx, ap.y + dy, ap.z + dz)
        if m is not None:
            # 是机器
            if not isinstance(m, ItemContainer):
                raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
            available_slots = m.output_slots
        else:
            container_size = GetContainerSize(cxyz, dim)
            if container_size is None:
                continue
            available_slots = range(container_size)
        for oslot in myslots:
            item = GetContainerItem(dim, xyz, oslot, getUserData=True)
            if item is not None and item.count >= item.GetBasicInfo().maxStackSize:
                continue
            for slot in available_slots:
                sitem = GetContainerItem(dim, cxyz, slot, getUserData=True)
                if sitem is None:
                    continue
                elif item is None:
                    if om is None or om.IsValidInput(oslot, sitem):
                        SetContainerItem(dim, cxyz, slot, Item("minecraft:air"))
                        # SetChestBoxItemNum(None, cxyz, slot, 0, dim)
                        SetContainerItem(dim, xyz, oslot, sitem)
                        item = sitem
                        ok = True
                elif item.CanMerge(sitem):
                    if om is not None and not om.IsValidInput(oslot, item):
                        continue
                    require_count = min(
                        item.GetBasicInfo().maxStackSize - item.count, sitem.count
                    )
                    count_overflow = max(0, sitem.count - require_count)
                    newitem = item.copy()
                    newitem.count = count_overflow
                    SetContainerItem(dim, cxyz, slot, newitem)
                    # SetChestBoxItemNum(None, cxyz, slot, count_overflow, dim)
                    item.count += require_count
                    SetContainerItem(dim, xyz, oslot, item)
                    ok = True
                if item is not None and item.count >= item.GetBasicInfo().maxStackSize:
                    break
    return ok


def clearNearbyContainersNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        ax, ay, az = x + dx, y + dy, z + dz
        containerNetworkPool.pop((dim, (ax, ay, az)), None)
        ap = containerAccessPointPool.pop((dim, x, y, z, facing), None)
        if ap is not None:
            bound_network = ap.get_bounded_network()
            if bound_network is not None:
                bound_network.group_inputs.discard(ap)
                bound_network.group_outputs.discard(ap)
            else:
                print("[ERROR] Cable access point {} bound network None".format((dim, x, y, z, facing)))

def UploadNetworkToPool(network):
    # type: (CableNetwork) -> None
    for ap in network.group_inputs:
        containerNetworkPool.setdefault((network.dim, (ap.x, ap.y, ap.z)), (set(), set()))[0].add(network)
    for ap in network.group_outputs:
        containerNetworkPool.setdefault((network.dim, (ap.x, ap.y, ap.z)), (set(), set()))[1].add(network)
    UpdateNetworkAccessPoints(network)

def UpdateNetworkAccessPoints(network):
    # type: (CableNetwork) -> None
    for ap in network.group_inputs | network.group_outputs:
        containerAccessPointPool[(network.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap

@ServerPlaceBlockEntityEvent.Listen()
def onBlockPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if BlockHasTag(event.blockName, "skybluetech_cable"):
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


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)

@BlockRemoveServerEvent.Listen()
@Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if event.fullName in COMMON_CONTAINERS:
        containerNetworkPool.pop((event.dimension, (event.x, event.y, event.z)), None)
    m = GetMachineWithoutCls(event.dimension, event.x, event.y, event.z)
    if m is not None:
        containerNetworkPool.pop((event.dimension, (event.x, event.y, event.z)), None)

@ContainerItemChangedServerEvent.Listen()
@Delay(ITEM_POST_DELAY)
def onContainerItemChanged(event):
    # type: (ContainerItemChangedServerEvent) -> None
    # 当容器内的物品变化时, 尝试将物品放入网络
    if event.pos is None:
        return
    dim = event.dimensionId
    x, y, z = xyz = event.pos
    if event.newItem.itemName == "minecraft:air" or event.newItem.count == 0:
        m = GetMachineStrict(dim, x, y, z)
        if not isinstance(m, ItemContainer):
            return
        if event.slot in m.input_slots:
            m.RequireItems()
    else:
        output_networks = GetContainerNetworks(dim, x, y, z, enable_cache=True)[1]
        m = GetMachineStrict(dim, x, y, z)  # 可能是一个机器
        if m is not None:
            if not isinstance(m, ItemContainer):
                raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
            if event.slot not in m.output_slots:
                return
            else:
                slots = m.output_slots
        else:
            slots = range(GetContainerSize(xyz, dim))
        for slot_not_empty in slots:
            item = GetContainerItem(dim, xyz, slot_not_empty, getUserData=True)
            if item is None:
                continue
            nitem = PostItemIntoNetworks(dim, xyz, item, output_networks)
            if nitem is not None:
                if nitem.count > 0:
                    if nitem.count == item.count:
                        continue
                    else:
                        SetContainerItem(dim, xyz, slot_not_empty, nitem)
                        if not POST_ALL_ITEMS_IN_ONE_TIME:
                            break
            else:
                SetContainerItem(dim, xyz, slot_not_empty, Item("minecraft:air", 0, 0))
                if not POST_ALL_ITEMS_IN_ONE_TIME:
                    break

@BlockNeighborChangedServerEvent.Listen()
def onNeighbourBlockChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.fromBlockName == event.toBlockName:
        return
    if not isCable(event.blockName):
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
        if isCable(event.toBlockName):
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
        clearNearbyContainersNetwork(
            event.dimensionId, event.neighborPosX, event.neighborPosY, event.neighborPosZ
        )
        GetContainerNetworks(
            event.dimensionId,
            event.neighborPosX, event.neighborPosY, event.neighborPosZ,
            enable_cache=False
        ) # 仅刷新
