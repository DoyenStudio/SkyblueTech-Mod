# coding=utf-8

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ContainerItemChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    BlockHasTag,
    GetBlockName,
    GetContainerItem,
    SetContainerItem,
    GetBlockEntityDataDict,
    GetContainerSize,
)
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from skybluetech_scripts.tooldelta.utils.py_comp import py2_xrange
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ..base.logic import LogicModule
from ..constants import COMMON_CONTAINERS
from .define import CableNetwork, CableAccessPoint

# TYPE_CHECKING
if 0:
    from typing import Iterable

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


def GetContainerSlotsCanInput(dim, pos, cacher):
    # type: (int, tuple[int, int, int], dict[tuple[int, int, int], Iterable[int]]) -> Iterable[int]
    cached = cacher.get(pos)
    if cached is not None:
        return cached
    m = GetMachineStrict(dim, *pos)
    if isinstance(m, ItemContainer):
        return m.input_slots
    block_name = GetBlockName(dim, pos)
    if block_name is None:
        return []
    elif block_name in COMMON_CONTAINERS:
        return py2_xrange(GetContainerSize(pos, dim))
    else:
        return []


def GetContainerSlotsCanOutput(dim, pos, cacher):
    # type: (int, tuple[int, int, int], dict[tuple[int, int, int], Iterable[int]]) -> Iterable[int]
    cached = cacher.get(pos)
    if cached is not None:
        return cached
    m = GetMachineStrict(dim, *pos)
    if isinstance(m, ItemContainer):
        return m.output_slots
    block_name = GetBlockName(dim, pos)
    if block_name is None:
        return []
    elif block_name in COMMON_CONTAINERS:
        return py2_xrange(GetContainerSize(pos, dim))
    else:
        return []


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    pass


MISSING = type("_MISSING", (), {})()


def _get_container_item(
    dim,  # type: int
    xyz,  # type: tuple[int, int, int]
    slot,  # type: int
    slotitem_cacher,  # type: dict[tuple[int, int, int], dict[int, Item | None]]
):
    # type: (...) -> Item | None
    cache = slotitem_cacher.get(xyz, {}).get(slot, MISSING)
    if cache is None or isinstance(cache, Item):
        return cache
    slotitem_cacher.setdefault((xyz), {})[slot] = res = GetContainerItem(
        dim, xyz, slot, getUserData=True
    )
    if res is None or res.count <= 0:
        return None
    return res


def onNetworkTick(network):
    # type: (CableNetwork) -> None
    tick_capacity = network.transfer_speed
    cached_block_entity_datas = {}  # type: dict[tuple[int, int, int], dict]
    cached_block_names = {}  # type: dict[tuple[int, int, int], str]
    cached_input_slot_poses = {}  # type: dict[tuple[int, int, int], Iterable[int]]
    cached_input_slotitems = {}  # type: dict[tuple[int, int, int], dict[int, Item | None]]
    input_slotitem_changed = {}  # type: dict[tuple[int, int, int], set[int]]
    cached_output_slot_poses = {}  # type: dict[tuple[int, int, int], Iterable[int]]
    cached_output_slotitems = {}  # type: dict[tuple[int, int, int], dict[int, Item | None]]
    output_slotitem_changed = {}  # type: dict[tuple[int, int, int], set[int]]
    inputs = network.get_input_access_points()
    outputs = network.get_output_access_points()

    def _get_container_input_slots(
        dim,  # type: int
        xyz,  # type: tuple[int, int, int]
    ):
        # type: (...) -> Iterable[int]
        cache = cached_input_slot_poses.get(xyz)
        if cache is not None:
            return cache
        m = GetMachineStrict(dim, *xyz)
        if isinstance(m, ItemContainer):
            cached_input_slot_poses[xyz] = res = m.input_slots
        else:
            cached_input_slot_poses[xyz] = res = py2_xrange(GetContainerSize(xyz, dim))
        return res

    def _get_container_output_slots(
        dim,  # type: int
        xyz,  # type: tuple[int, int, int]
    ):
        # type: (...) -> Iterable[int]
        cache = cached_output_slot_poses.get(xyz)
        if cache is not None:
            return cache
        m = GetMachineStrict(dim, *xyz)
        if isinstance(m, ItemContainer):
            cached_output_slot_poses[xyz] = res = m.output_slots
        else:
            cached_output_slot_poses[xyz] = res = py2_xrange(GetContainerSize(xyz, dim))
        return res

    def _get_block_entity_data(dim, xyz):
        # type: (int, tuple[int, int, int]) -> dict
        res = cached_block_entity_datas.get(xyz)
        if res is None:
            res = cached_block_entity_datas[xyz] = (
                GetBlockEntityDataDict(dim, xyz) or {}
            )
        return res

    def _get_block_name(dim, xyz):
        # type: (int, tuple[int, int, int]) -> str | None
        res = cached_block_names.get(xyz)
        if res is None:
            res = cached_block_names[xyz] = GetBlockName(dim, xyz) or ""
        return res

    # TODO: 性能优化

    break_flag1 = False
    for output_ap in outputs:
        output_pos = output_ap.target_pos
        output_slotposes = _get_container_output_slots(network.dim, output_pos)

        if _get_block_name(network.dim, output_pos) == "minecraft:chest":
            pair_x = GetValueWithDefault(
                _get_block_entity_data(network.dim, output_pos), "pairx", None
            )
            pair_z = GetValueWithDefault(
                _get_block_entity_data(network.dim, output_pos), "pairz", None
            )
        else:
            pair_x = pair_z = None

        for output_slot in output_slotposes:
            output_item = _get_container_item(
                network.dim, output_pos, output_slot, cached_output_slotitems
            )
            if output_item is None:
                continue

            count_to_send = min(tick_capacity, output_item.count)
            count_cant_send = output_item.count - count_to_send
            output_item.count = count_to_send

            for input_ap in inputs:
                input_pos = input_ap.target_pos

                if _get_block_name(network.dim, input_pos) == "minecraft:chest":
                    x, _, z = input_pos
                    if pair_x == x and pair_z == z:
                        continue
                if input_pos == output_pos:
                    continue

                break_flag2 = False
                input_slotposes = _get_container_input_slots(network.dim, input_pos)
                for input_slot in input_slotposes:
                    input_item = _get_container_item(
                        network.dim, input_pos, input_slot, cached_input_slotitems
                    )
                    if input_item is None:
                        cached_input_slotitems[input_pos][input_slot] = (
                            output_item.copy()
                        )
                        output_item.count = 0
                    elif (
                        input_item.CanMerge(output_item) and not input_item.StackFull()
                    ):
                        # print "Slot", input_slot, input_item.marshal()
                        input_item.MergeFrom(output_item)
                        cached_input_slotitems[input_pos][input_slot] = input_item
                    else:
                        continue

                    input_slotitem_changed.setdefault(input_pos, set()).add(input_slot)
                    output_slotitem_changed.setdefault(output_pos, set()).add(
                        output_slot
                    )

                    tick_capacity -= count_to_send - output_item.count
                    output_item.count += count_cant_send

                    if output_item.count <= 0:
                        # 输出槽物品已全部投递
                        cached_output_slotitems[output_pos][output_slot] = None
                        break_flag2 = True
                        break
                    else:
                        cached_output_slotitems[output_pos][output_slot] = output_item
                    if tick_capacity <= 0:
                        break_flag1 = break_flag2 = True
                        break

                if break_flag2:
                    break
        if break_flag1:
            break

    for pos, changed_slots in output_slotitem_changed.items():
        for slot in changed_slots:
            item = cached_output_slotitems[pos][slot]
            if item is None:
                SetContainerItem(network.dim, pos, slot, Item("minecraft:air"))
            else:
                SetContainerItem(network.dim, pos, slot, item)

    for pos, changed_slots in input_slotitem_changed.items():
        for slot in changed_slots:
            item = cached_input_slotitems[pos][slot]
            if item is None:
                SetContainerItem(network.dim, pos, slot, Item("minecraft:air"))
            else:
                SetContainerItem(network.dim, pos, slot, item)

    # print input_slotitem_changed, output_slotitem_changed


logic_module = LogicModule(
    CableNetwork,
    CableAccessPoint,
    transmitter_check_func=isCable,
    transmittable_block_check_func=isContainer,
    on_transmittable_block_placed_later=onMachineryPlacedLater,
    on_network_tick=onNetworkTick,
)


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)
