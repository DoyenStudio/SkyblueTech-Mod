# coding=utf-8
#
from collections import deque
from weakref import WeakValueDictionary as WValueDict
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    BlockNeighborChangedServerEvent,
    ContainerItemChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    BlockHasTag,
    GetBlockStates,
    UpdateBlockStates,
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
from .pool import CableNetworkPool, CableAccessPointPool, GNodes

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
    nodes = set() # type: set[PosData]

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
                if block_states["skybluetech:cable_io_" + dir_name]:
                    _o.add(CableAccessPoint(dim, cx, cy, cz, facing, AP_MODE_OUTPUT))
                else:
                    _i.add(CableAccessPoint(dim, cx, cy, cz, facing, AP_MODE_INPUT))

        input_nodes |= _i
        output_nodes |= _o
        connected.add(
            current
        )  # TODO: 管道过多使得队列内存占用过大; 考虑限制最大 bfs 数
        nodes.add(current)
    return CableNetwork(
        dim,
        input_nodes,
        output_nodes,
        nodes,
        0,  # 目前无传输限制,
    )

def getAndInitNetwork(dim, start, exists=None):
    # type: (int, PosData, set[PosData] | None) -> CableNetwork | None
    """
    在管道位置获取并初始化传输网络。

    Args:
        dim (int): 维度 ID
        start (tuple[int, int, int]): 开始坐标
        exists (set, optional): 用于缓存路径点的set

    Returns:
        CableNetwork (optional): 传输网络
    """
    network = bfsFindConnections(dim, start, exists)
    if network is None:
        return None
    dim_datas = GNodes.setdefault(dim, WValueDict())
    for node in network.nodes:
        dim_datas[node] = network
    for ap in network.group_inputs | network.group_outputs:
        CableAccessPointPool[(network.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap
    return network

def cleanNearbyNetwork(dim, x, y, z):
    # type: (int, int, int, int) -> None
    """
    清理一个容器附近的所有传输网络。
    一般是容器消失时调用的。

    Args:
        dim (int): 维度 ID
        x (int): x
        y (int): y
        z (int): z
    """
    CableNetworkPool.pop((dim, (x, y, z)), None)
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        opposite_facing = OPPOSITE_FACING[facing]
        ax, ay, az = x + dx, y + dy, z + dz
        ap = CableAccessPointPool.pop((dim, ax, ay, az, opposite_facing), None)
        if ap is not None:
            bound_network = ap.get_bounded_network()
            if bound_network is not None:
                bound_network.group_inputs.discard(ap)
                bound_network.group_outputs.discard(ap)
            else:
                print("[ERROR] Cable access point {} bound network None".format((dim, x, y, z, facing)))

def deleteNetwork(network):
    # type: (CableNetwork) -> None
    "完全清除一个网络。"
    for ap in network.group_inputs | network.group_outputs:
        CableAccessPointPool.pop((network.dim, ap.x, ap.y, ap.z, ap.access_facing), None)
        nws = CableNetworkPool.get((network.dim, ap.target_pos))
        if nws is None:
            continue
        i, o = nws
        if network in i:
            i.remove(network)
        elif network in o:
            o.remove(network)
        if not i and not o:
            CableNetworkPool.pop((network.dim, ap.target_pos), None)
    for node in network.nodes.copy():
        GNodes.get(network.dim, {}).pop(node, None)

def cleanAccessPoint(dim, x, y, z):
    """
    清理一个节点的网络数据。

    Args:
        dim (int): 维度 ID
        x (int): x
        y (int): y
        z (int): z
    """
    network = GNodes.get(dim, {}).pop((x, y, z), None) or GetNetworkByCable(dim, x, y, z)
    if network is not None:
        deleteNetwork(network)
    tmp_set = set()
    GetNearbyCableNetworks(
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
    i, o = GetNearbyCableNetworks(dim, x, y, z)
    for network in i + o:
        deleteNetwork(network)
    tmp_set = set()
    GetNetworkByCable(
        dim,
        x,
        y,
        z,
        tmp_set
    )
    GetNearbyCableNetworks(
        dim,
        x,
        y,
        z,
        tmp_set,
        enable_cache=False
    ) # 仅刷新

def GetNearbyCableNetworks(dim, x, y, z, exists=None, enable_cache=True):
    # type: (int, int, int, int, set[PosData] | None, bool) -> tuple[list[CableNetwork], list[CableNetwork]]
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
        tuple[set[CableNetwork], set[CableNetwork]]: 分别表示输入和提取模式的传输网络
    """
    if enable_cache:
        cached_network = CableNetworkPool.get((dim, (x, y, z)), None)
        if cached_network is not None and cached_network[0] and cached_network[1]:
            # not pretty fix
            return cached_network
    input_networks = []  # type: list[CableNetwork]
    output_networks = []  # type: list[CableNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        old_network = GNodes.get(dim, {}).get(next_pos)
        network = getAndInitNetwork(dim, next_pos, _exists)
        if network is None:
            continue
        if old_network is not None:
            old_network.flush_from(network)
        p = CableAccessPoint(dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1) # -1 表示输入输出模式未知
        if p in network.group_inputs:
            input_networks.append(network)
        elif p in network.group_outputs:
            output_networks.append(network)
    CableNetworkPool[(dim, (x, y, z))] = (input_networks, output_networks)
    return input_networks, output_networks

def GetNetworkByCable(dim, x, y, z, cacher=None):
    # type: (int, int, int, int, set[PosData] | None) -> CableNetwork | None
    network = GNodes.get(dim, {}).get((x, y, z))
    if network is not None:
        return network
    return getAndInitNetwork(dim, (x, y, z), cacher)

def PostItemIntoNetworks(dim, xyz, item, networks):
    # type: (int, tuple[int, int, int], Item, list[CableNetwork] | None) -> None | Item
    "向网络发送物品, 返回剩余物品"
    if networks is None:
        x, y, z = xyz
        networks = GetNearbyCableNetworks(dim, x, y, z, enable_cache=True)[1]
    for ap in sorted(
        [i for network in networks for i in network.group_inputs],
        key=lambda ap: ap.get_priority(),
        reverse=True,
    ):
        if xyz == ap.target_pos:
            # 别自己给自己装东西 !
            continue
        ret_item = PushItemToGenericContainer(ap, item)
        if ret_item is None:
            return None
        else:
            item = ret_item
    return item

def PushItemToGenericContainer(ap, item):
    # type: (CableAccessPoint, Item) -> Item | None
    cxyz = ap.target_pos
    m = GetMachineWithoutCls(ap.dim, *cxyz)
    if m is not None:
        # 是机器
        if not isinstance(m, ItemContainer):
            raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
        return m.PushItem(item)
    else:
        container_size = GetContainerSize(cxyz, ap.dim)
        if container_size is None:
            return item
        return PushItemToOrigContainer(ap.dim, cxyz, item, container_size)

def PushItemToOrigContainer(dim, xyz, item, container_size):
    # type: (int, tuple[int, int, int], Item, int) -> Item | None
    for slot_pos in range(container_size):
        orig_item = GetContainerItem(dim, xyz, slot_pos, getUserData=True)
        if orig_item is None:
            res = SetContainerItem(dim, xyz, slot_pos, item)
            if res:
                return None
            else:
                continue
        elif not orig_item.CanMerge(item):
            continue
        sum_count = orig_item.count + item.count
        max_stack = orig_item.GetBasicInfo().maxStackSize
        if sum_count > max_stack:
            item_new = item.copy()
            item_new.count = max_stack
            res = SetContainerItem(dim, xyz, slot_pos, item_new)
            if not res:
                continue
            item.count = sum_count - max_stack
        else:
            item_new = item.copy()
            item_new.count = sum_count
            res = SetContainerItem(dim, xyz, slot_pos, item_new)
            if not res:
                continue
            return None
    return item

def RequireItems(dim, xyz):
    # type: (int, tuple[int, int, int]) -> bool
    "在某一个坐标的容器向周围的网络请求物品。"
    x, y, z = xyz
    networks = GetNearbyCableNetworks(dim, x, y, z, enable_cache=True)[0]
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

@ServerPlaceBlockEntityEvent.Listen()
def onBlockPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if isCable(event.blockName):
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
        cleanAccessPoint(event.dimension, event.posX, event.posY, event.posZ)
    elif isContainer(event.blockName):
        # 图方便
        cleanContainerNetworks(event.dimension, event.posX, event.posY, event.posZ)


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)

@BlockRemoveServerEvent.Listen()
@Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
def onBlockRemoved(event):
    # type: (BlockRemoveServerEvent) -> None
    if isContainer(event.fullName):
        cleanNearbyNetwork(event.dimension, event.x, event.y, event.z)
    if isCable(event.fullName):
        cleanAccessPoint(event.dimension, event.x, event.y, event.z)

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
        output_networks = GetNearbyCableNetworks(dim, x, y, z, enable_cache=True)[1]
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
