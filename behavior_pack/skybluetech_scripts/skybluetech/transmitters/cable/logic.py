# coding=utf-8
#
from collections import deque
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockRemoveServerEvent,
    ServerPlaceBlockEntityEvent,
    ServerBlockUseEvent,
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.events.server.item import (
    ContainerItemChangedServerEvent,
)
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    BlockHasTag,
    GetBlockStates,
    UpdateBlockStates,
    AddBlocksToBlockRemoveListener,
)
from skybluetech_scripts.tooldelta.api.server.container import (
    GetContainerItem,
    SetContainerItem,
    GetContainerSize,
    # SetChestBoxItemNum,
)
from skybluetech_scripts.tooldelta.api.timer import Delay
from skybluetech_scripts.tooldelta.api.server.tips import SetOnePopupNotice
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ...define.utils import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..constants import COMMON_CONTAINERS, FACING_EN, FACING_ZHCN, DXYZ_FACING
from .define import CableNetwork
from .pool import containerNetworkPool, GetSameNetwork

# TYPE_CHECKING
if TYPE_CHECKING:
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


def bfsFindConnections(dim, start, connected=None):
    # type: (int, PosData, set[PosData] | None) -> CableNetwork | None
    # 从某一管道开始, 建立管道网络
    # 确保 start 一定是管道 !!!

    start_bname = GetBlockName(dim, start)
    if start_bname is None:
        return None
    if not isCable(start_bname):  # 确保 start 一定是管道 !!!
        return None

    output_nodes = set()  # type: set[PosDataWithFacing] # 最后一个 int 表示线缆是通过哪个面接入容器的
    input_nodes = set()  # type: set[PosDataWithFacing]
    if connected is None:
        connected = set()

    first_cable_name = None

    queue = deque([start])
    while queue:
        current = queue.popleft()
        cx, cy, cz = current
        block_states = GetBlockStates(dim, current)

        _i = set()  # type: set[PosDataWithFacing]
        _o = set()  # type: set[PosDataWithFacing]
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
            dir_name = FACING_EN[facing]
            if block_states["skybluetech:connection_" + dir_name]:
                if block_states["skybluetech:cable_io_" + dir_name]:
                    _o.add(current + (facing,))
                else:
                    _i.add(current + (facing,))

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


def getNearbyCableNetwork(dim, x, y, z, exists=None):
    # type: (int, int, int, int, set[PosData] | None) -> tuple[set[CableNetwork], set[CableNetwork]]
    input_networks = set()  # type: set[CableNetwork]
    output_networks = set()  # type: set[CableNetwork]
    _exists = exists or set()  # type: set[PosData]
    for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
        next_pos = (x + dx, y + dy, z + dz)
        network = bfsFindConnections(dim, next_pos, _exists)
        if network is None:
            continue
        p = next_pos + (OPPOSITE_FACING[facing],)
        if p in network.group_inputs:
            input_networks.add(GetSameNetwork(network))
        elif p in network.group_outputs:
            output_networks.add(GetSameNetwork(network))
    return input_networks, output_networks


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
    return nws


def PostItemIntoNetworks(dim, xyz, item, networks):
    # type: (int, tuple[int, int, int], Item, set[CableNetwork] | None) -> None | Item
    "向网络发送物品, 返回剩余物品"
    if networks is None:
        x, y, z = xyz
        networks = GetContainerNetworks(dim, x, y, z, enable_cache=True)[1]
    stack_size = item.GetBasicInfo().maxStackSize
    for cx, cy, cz, facing in (i for network in networks for i in network.group_inputs):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[facing]
        cxyz = (cx + dx, cy + dy, cz + dz)
        if xyz == cxyz:
            # 别自己给自己装东西 !
            continue
        m = GetMachineWithoutCls(dim, cx + dx, cy + dy, cz + dz)
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
    for cx, cy, cz, facing in (
        i for network in networks for i in network.group_outputs
    ):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[facing]
        cxyz = (cx + dx, cy + dy, cz + dz)
        if xyz == cxyz:
            # 别自己给自己提取 !
            continue
        m = GetMachineWithoutCls(dim, cx + dx, cy + dy, cz + dz)
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


def AddNetworkToPool(dim, network):
    # type: (int, CableNetwork) -> None
    for x, y, z, _ in network.group_inputs:
        containerNetworkPool.setdefault((dim, (x, y, z)), (set(), set()))[0].add(network)
    for x, y, z, _ in network.group_outputs:
        containerNetworkPool.setdefault((dim, (x, y, z)), (set(), set()))[1].add(network)


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
                        # 没有任何容器供塞入
                        continue
                    else:
                        SetContainerItem(dim, xyz, slot_not_empty, nitem)
                        if not POST_ALL_ITEMS_IN_ONE_TIME:
                            break
            else:
                SetContainerItem(dim, xyz, slot_not_empty, Item("minecraft:air", 0, 0))
                if not POST_ALL_ITEMS_IN_ONE_TIME:
                    break


PIECE = 5.0 / 16


@ServerBlockUseEvent.Listen()
def onPlayerUseWrench(event):
    # type: (ServerBlockUseEvent) -> None
    if (
        event.blockName != "skybluetech:item_transport_cable"
        or event.item.newItemName != "skybluetech:transmitter_wrench"
    ):
        return
    blockX = event.x
    blockY = event.y
    blockZ = event.z
    clickX = event.clickX
    clickY = event.clickY
    clickZ = event.clickZ
    block_orig_status = GetBlockStates(event.dimensionId, (blockX, blockY, blockZ))
    if clickY > 0 and clickY < PIECE:
        facing = 0  # down
    elif clickY > 1 - PIECE and clickY < 1:
        facing = 1
    elif clickZ > 0 and clickZ < PIECE:
        facing = 2  # north
    elif clickZ > 1 - PIECE and clickZ < 1:
        facing = 3  # south
    elif clickX > 0 and clickX < PIECE:
        facing = 4  # west
    elif clickX > 1 - PIECE and clickX < 1:
        facing = 5  # east
    else:
        SetOnePopupNotice(event.playerId, "无效扳手调节位置")
        return
    dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[facing]
    nextBlock = GetBlockName(event.dimensionId, (blockX + dx, blockY + dy, blockZ + dz))
    if nextBlock is None or isCable(nextBlock):
        SetOnePopupNotice(
            event.playerId,
            "§6无法为已连接了另外一根管道的管道设置传输模式",
            "§7[§cx§7] §c错误",
        )
        return
    elif not canConnect(nextBlock):
        SetOnePopupNotice(
            event.playerId, "§6无法为未连接的管道设置传输模式", "§7[§cx§7] §c错误"
        )
        return
    facing_en_key = "skybluetech:cable_io_" + FACING_EN[facing]
    newState = not block_orig_status.get(facing_en_key, False)
    block_orig_status[facing_en_key] = newState
    current_network = bfsFindConnections(event.dimensionId, (blockX, blockY, blockZ))
    if current_network is None:
        SetOnePopupNotice(event.playerId, "§4管道数据异常", "§7[§cx§7] §c错误")
        return
    if newState:
        current_network.group_inputs.remove((blockX, blockY, blockZ, facing))
        current_network.group_outputs.add((blockX, blockY, blockZ, facing))
    else:
        current_network.group_inputs.add((blockX, blockY, blockZ, facing))
        current_network.group_outputs.remove((blockX, blockY, blockZ, facing))
    SetOnePopupNotice(
        event.playerId,
        "§f已将管道的§6"
        + FACING_ZHCN[facing]
        + "§f面设置为"
        + ("§a输入", "§c抽出")[newState],
    )
    UpdateBlockStates(event.dimensionId, (blockX, blockY, blockZ), block_orig_status)


AddBlocksToBlockRemoveListener(COMMON_CONTAINERS)


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
            event.dimensionId, event.posX, event.posY, event.posZ
        )
        cacher = set()  # type: set[PosData]
        i, o = GetContainerNetworks(
            event.dimensionId,
            event.posX, event.posY, event.posZ,
            cacher=cacher,
            enable_cache=False
        )
        for network in i | o:
            AddNetworkToPool(event.dimensionId, network)
