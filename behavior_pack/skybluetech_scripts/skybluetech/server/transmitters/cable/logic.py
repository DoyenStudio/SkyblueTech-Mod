# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ContainerItemChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server import BlockHasTag
from skybluetech_scripts.tooldelta.api.server.container import (
    GetContainerItem,
    SetContainerItem,
    GetContainerSize,
)
from skybluetech_scripts.tooldelta.api.common import Delay
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ....common.define.facing import NEIGHBOR_BLOCKS_ENUM
from ..base.logic import LogicModule
from ..constants import COMMON_CONTAINERS
from .define import CableNetwork, CableAccessPoint

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

# TODO: 在快速取走物品时物品管道有可能不会继续传输物品


def isCable(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_cable")


def isContainer(blockName):
    return blockName in COMMON_CONTAINERS or BlockHasTag(
        blockName, "skybluetech_container"
    )


def PostItemIntoNetworks(dim, xyz, item, networks):
    # type: (int, tuple[int, int, int], Item, set[CableNetwork] | None) -> None | Item
    "向网络发送物品, 返回剩余物品"
    item = item.copy()
    if networks is None:
        x, y, z = xyz
        networks = set(
            i
            for i in logic_module.GetContainerNode(
                dim, x, y, z, enable_cache=True
            ).outputs.values()
            if i is not None
        )
    for network in networks:
        transfer_speed = network.transfer_speed
        for ap in network.get_input_access_points():
            if xyz == ap.target_pos:
                # 别自己给自己装东西 !
                continue
            ret_item = PushItemToGenericContainer(ap, item, transfer_speed)
            if ret_item is None:
                return None
            item = ret_item
    return item


def PushItemToGenericContainer(ap, item, limit_count=None):
    # type: (CableAccessPoint, Item, int | None) -> Item | None
    cxyz = ap.target_pos
    send_item = item.copy()
    if limit_count is not None:
        send_item.count = min(send_item.count, limit_count)
    overflow_count = item.count - send_item.count
    m = GetMachineWithoutCls(ap.dim, *cxyz)
    if m is not None:
        # 是机器
        if not isinstance(m, ItemContainer):
            raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
        res = m.PushItem(send_item)
    else:
        container_size = GetContainerSize(cxyz, ap.dim)
        if container_size is None:
            return item
        res = PushItemToOrigContainer(ap.dim, cxyz, send_item, container_size)
    if res is None:
        if overflow_count <= 0:
            return None
        else:
            send_item.count = overflow_count
    else:
        send_item.count += overflow_count
    return send_item


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


require_item_queue = set()  # type: set[tuple[int, tuple[int, int, int]]]


def RequireItems(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    "在某一个坐标的容器向周围的网络请求物品。"
    k = (dim, xyz)
    if k in require_item_queue:
        return
    require_item_queue.add((dim, xyz))
    _require_items(dim, xyz)


def _require_items(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    require_item_queue.discard((dim, xyz))
    x, y, z = xyz
    cnode = logic_module.GetContainerNode(dim, x, y, z, enable_cache=True)
    networks = [i for i in cnode.inputs.values() if i is not None]
    for ap in sorted(
        (i for network in networks for i in network.group_outputs),
        key=lambda ap: ap.get_priority(),
    ):
        cxyz = ap.target_pos
        if xyz == cxyz:
            # 别自己给自己提取 !
            continue
        ContainerPostItem(dim, cxyz)


def onActivateNetwork(network):
    # type: (CableNetwork) -> None
    for ap in network.get_input_access_points():
        target_pos = ap.target_pos
        RequireItems(network.dim, target_pos)


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    # 在容器被放置后延迟执行,
    # 用于使新容器尝试接收一次物品
    RequireItems(dim, (x, y, z))


event_queue = set()  # type: set[tuple[int, tuple[int, int, int]]]


@ContainerItemChangedServerEvent.Listen()
@Delay(0)
def onContainerItemChanged(event):
    # type: (ContainerItemChangedServerEvent) -> None
    # 当容器内的物品变化时, 尝试将物品放入网络
    if event.pos is None:
        return
    dim = event.dimensionId
    xyz = event.pos
    if event.newItem.count == 0:
        m = GetMachineStrict(dim, *xyz)
        if isinstance(m, ItemContainer):
            if event.slot in m.input_slots:
                RequireItems(dim, xyz)
        else:
            RequireItems(dim, xyz)
    ContainerPostItem(dim, xyz)


def ContainerPostItem(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    m = GetMachineStrict(dim, *xyz)  # 可能是一个机器
    if m is not None:
        if not isinstance(m, ItemContainer):
            raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
        else:
            slots = m.output_slots
    else:
        slots = range(GetContainerSize(xyz, dim))
    k = (dim, xyz)
    if k in event_queue:
        return
    event_queue.add((dim, xyz))
    _cotainerPostItems(dim, xyz, slots)  # pyright: ignore[reportArgumentType]


@Delay(ITEM_POST_DELAY)
def _cotainerPostItems(dim, xyz, slots):
    # type: (int, tuple[int, int, int], tuple[int, ...]) -> None
    event_queue.discard((dim, xyz))
    x, y, z = xyz
    output_networks = set(
        i
        for i in logic_module.GetContainerNode(
            dim, x, y, z, enable_cache=True
        ).outputs.values()
        if i is not None
    )
    for slot_not_empty in slots:
        item = GetContainerItem(dim, xyz, slot_not_empty, getUserData=True)
        if item is None:
            continue
        rest_item = PostItemIntoNetworks(dim, xyz, item, output_networks)
        if rest_item is not None:
            if rest_item.count > 0:
                if rest_item.count == item.count:
                    continue
                else:
                    res = SetContainerItem(dim, xyz, slot_not_empty, rest_item)
                    if not res:
                        print("[Warning] SetItem to container %d %d %d failed" % xyz)
                    if not POST_ALL_ITEMS_IN_ONE_TIME:
                        break
        else:
            SetContainerItem(dim, xyz, slot_not_empty, Item("minecraft:air", 0, 0))
            # if not POST_ALL_ITEMS_IN_ONE_TIME:
            #     break


logic_module = LogicModule(
    CableNetwork,
    CableAccessPoint,
    isCable,
    isContainer,
    onMachineryPlacedLater,
    onActivateNetwork,
)


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)
