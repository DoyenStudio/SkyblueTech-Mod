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
from skybluetech_scripts.tooldelta.api.timer import Delay
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ...define.facing import NEIGHBOR_BLOCKS_ENUM
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
        send_item = item.copy()
        if transfer_speed is not None:
            send_item.count = min(item.count, transfer_speed)
        for ap in network.get_input_access_points():
            if xyz == ap.target_pos:
                # 别自己给自己装东西 !
                continue
            ret_item = PushItemToGenericContainer(ap, send_item)
            if ret_item is not None:
                item.count = send_item.count - ret_item.count
            else:
                item.count -= send_item.count
            if item.count == 0:
                return None
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
    networks = (
        i
        for i in logic_module.GetContainerNode(
            dim, x, y, z, enable_cache=True
        ).outputs.values()
        if i is not None
    )
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
def onContainerItemChanged(event):
    # type: (ContainerItemChangedServerEvent) -> None
    # 当容器内的物品变化时, 尝试将物品放入网络
    if event.pos is None:
        return
    k = (event.dimensionId, event.pos)
    if k in event_queue:
        return
    event_queue.add(k)
    CotainerPostItem(event.dimensionId, event.pos, event.slot, event.newItem)


@Delay(ITEM_POST_DELAY)
def CotainerPostItem(dim, xyz, slot, slotitem):
    # type: (int, tuple[int, int, int], int, Item) -> None
    x, y, z = xyz
    event_queue.discard((dim, xyz))
    if slotitem.id == "minecraft:air" or slotitem.count == 0:
        m = GetMachineStrict(dim, x, y, z)
        if not isinstance(m, ItemContainer):
            return
        if slot in m.input_slots:
            m.RequireItems()
    output_networks = set(
        i
        for i in logic_module.GetContainerNode(
            dim, x, y, z, enable_cache=True
        ).outputs.values()
        if i is not None
    )
    m = GetMachineStrict(dim, x, y, z)  # 可能是一个机器
    if m is not None:
        if not isinstance(m, ItemContainer):
            raise ValueError("Machine %s is not a ItemContainer" % type(m).__name__)
        if slot not in m.output_slots:
            return
        else:
            slots = m.output_slots
    else:
        slots = range(GetContainerSize(xyz, dim))
    if not output_networks:
        return
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
                    res = SetContainerItem(dim, xyz, slot_not_empty, nitem)
                    if not res:
                        print("[Warning] SetItem to container %d %d %d failed" % xyz)
                    if not POST_ALL_ITEMS_IN_ONE_TIME:
                        break
        else:
            SetContainerItem(dim, xyz, slot_not_empty, Item("minecraft:air", 0, 0))
            if not POST_ALL_ITEMS_IN_ONE_TIME:
                break


logic_module = LogicModule(
    CableNetwork,
    CableAccessPoint,
    isCable,
    isContainer,
    onMachineryPlacedLater,
    onActivateNetwork,
)


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)
