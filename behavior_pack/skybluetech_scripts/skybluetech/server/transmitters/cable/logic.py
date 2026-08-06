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
    GetContainerSize,
    SetBlockEntityData,
)
from skybluetech_scripts.tooldelta.utils.nbt import (
    Byte,
    GetValueWithDefault,
    Py2NBT,
    Short,
    String,
)
from skybluetech_scripts.tooldelta.utils.py_comp import py2_xrange
from ...machinery.basic.item_container import ItemContainer
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls
from ..base.logic import LogicModule
from ..constants import COMMON_CONTAINERS
from .define import CableNetwork, CableAccessPoint
from .nbt_utils import (
    MISSING,
    _find_slot_entry,
    _get_container_nbt,
    _item_to_nbt_entry,
    _nbt_entry_to_item,
)

# TYPE_CHECKING
if 0:
    import typing

    PosData = typing.Tuple[int, int, int]  # x y z
    PosDataWithFacing = typing.Tuple[int, int, int, int]  # x y z facing
# TYPE_CHECKING END

# 输入型网络: 网络向此容器输入物品
# 输出型网络: 网络向此容器提取物品

# todo: 后续优化:
#       1. 添加物品过滤功能
#       2. 如果找到了可投递的容器, 下次优先向此容器进行投递, 提高命中率


def isCable(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_cable")


def isContainer(blockName, dim=None, xyz=None):
    # type: (str, int | None, tuple[int, int, int] | None) -> bool
    "方块是否为可连接的物品容器: 只要能获取到容器大小即可连接。"
    if dim is not None and xyz is not None:
        size = GetContainerSize(xyz, dim)
        if size is not None and size > 0:
            return True
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
            for i in logic_module
            .GetContainerNode(dim, x, y, z, enable_cache=True)
            .get_outputs()
            .values()
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
    if m is not None and isinstance(m, ItemContainer):
        # 是物品容器机器: 按机器槽位逻辑投递
        res = m.PushItem(send_item)
    else:
        # 非机器或未声明物品槽位的机器: 一律按普通容器逻辑
        container_size = GetContainerSize(cxyz, ap.dim)
        if container_size is None or container_size <= 0:
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
            max_stack = item.GetBasicInfo().maxStackSize
            if item.count <= max_stack:
                res = SetContainerItem(dim, xyz, slot_pos, item)
                if res:
                    return None
                else:
                    continue
            item_new = item.copy()
            item_new.count = max_stack
            res = SetContainerItem(dim, xyz, slot_pos, item_new)
            if not res:
                continue
            item.count -= max_stack
        elif not orig_item.CanMerge(item) or orig_item.StackFull():
            continue
        else:
            require_count = min(
                orig_item.GetBasicInfo().maxStackSize - orig_item.count, item.count
            )
            orig_item.count += require_count
            item.count -= require_count
            res = SetContainerItem(dim, xyz, slot_pos, orig_item)
            if not res:
                continue
            if item.count == 0:
                return None
    return item


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    pass


def onNetworkTick(network):
    # type: (CableNetwork) -> None
    tick_capacity = network.transfer_speed
    slotitem_changed = {}  # type: dict[tuple[int, int, int], set[int]]
    inputs = network.get_input_access_points()
    outputs = network.get_output_access_points()

    if tick_capacity <= 0 or not outputs:
        return

    # 输出端轮询游标: 每次 tick 从下一个接入点开始扫描, 避免单个输出端长期独占容量
    output_count = len(outputs)
    start = network._output_cursor % output_count
    network._output_cursor = (start + 1) % output_count

    break_flag1 = False
    for output_index in range(output_count):
        output_ap = outputs[(start + output_index) % output_count]
        output_pos = output_ap.target_pos
        output_slotposes = _get_container_output_slots(network, output_pos)

        if _get_block_name(network, output_pos) == "minecraft:chest":
            pair_data, _ = _get_container_nbt(
                network.dim, output_pos, network._cache_datas
            )
            pair_x = GetValueWithDefault(pair_data or {}, "pairx", None)
            pair_z = GetValueWithDefault(pair_data or {}, "pairz", None)
            pair_y = output_pos[1]
        else:
            pair_x = pair_z = pair_y = None

        for output_slot in output_slotposes:
            output_item = _get_container_item(network, output_pos, output_slot)
            if output_item is None:
                continue

            count_to_send = min(tick_capacity, output_item.count)
            if count_to_send <= 0:
                break
            send_item = output_item.copy()
            send_item.count = count_to_send

            for input_ap in inputs:
                input_pos = input_ap.target_pos

                if input_pos == output_pos:
                    continue
                if (
                    _get_block_name(network, input_pos) == "minecraft:chest"
                    and pair_x == input_pos[0]
                    and pair_z == input_pos[2]
                    and pair_y == input_pos[1]
                ):
                    # 跳过双箱子的另一半, 避免同一容器互相搬运
                    continue

                m = GetMachineStrict(network.dim, *input_pos)

                break_flag2 = False
                input_slotposes = _get_container_input_slots(network, input_pos)
                for input_slot in input_slotposes:
                    if isinstance(m, ItemContainer):
                        if not m.IsValidInput(input_slot, send_item):
                            continue
                    input_item = _get_container_item(network, input_pos, input_slot)
                    if input_item is None:
                        move_count = min(
                            send_item.count, send_item.GetBasicInfo().maxStackSize
                        )
                        input_item = send_item.copy()
                        input_item.count = move_count
                        network._cache_slotitems[input_pos][input_slot] = input_item
                        send_item.count -= move_count
                    elif input_item.CanMerge(send_item) and not input_item.StackFull():
                        # print "Slot", input_slot, input_item.marshal()
                        before_count = send_item.count
                        input_item.MergeFrom(send_item)
                        move_count = before_count - send_item.count
                        if move_count <= 0:
                            continue
                        network._cache_slotitems[input_pos][input_slot] = input_item
                    else:
                        continue

                    output_item.count -= move_count
                    tick_capacity -= move_count

                    slotitem_changed.setdefault(input_pos, set()).add(input_slot)
                    slotitem_changed.setdefault(output_pos, set()).add(output_slot)

                    if output_item.count <= 0:
                        # 输出槽物品已全部投递
                        network._cache_slotitems[output_pos][output_slot] = None
                        break_flag2 = True
                        break
                    else:
                        network._cache_slotitems[output_pos][output_slot] = output_item
                    if tick_capacity <= 0:
                        break_flag1 = break_flag2 = True
                        break
                    if send_item.count <= 0:
                        # 物品已全部投递, 无需再扫描其他输入接入点
                        break_flag2 = True
                        break

                if break_flag2:
                    break
        if break_flag1:
            break

    for pos, changed_slots in slotitem_changed.items():
        slotitems = network._cache_slotitems.get(pos)
        if slotitems is None:
            # 缓存中途被外部事件失效, 放弃本次写回, 下次 tick 重新读取
            continue
        data, items = _get_container_nbt(network.dim, pos, network._cache_datas)
        if data is None:
            continue
        for slot in changed_slots:
            item = slotitems.get(slot, MISSING)
            if item is MISSING:
                continue
            list_index, _ = _find_slot_entry(items, slot)
            if item is None:
                if list_index >= 0:
                    items.pop(list_index)
            elif list_index >= 0:
                # 原地更新条目, 保留 Block/WasPickedUp 等额外字段
                old_entry = items[list_index]
                old_entry["Count"] = Byte(item.count)
                old_entry["Name"] = String(item.newItemName)
                old_entry["Damage"] = Short(item.newAuxValue)
                if item.userData is not None:
                    old_entry["tag"] = Py2NBT(item.userData)
                else:
                    old_entry.pop("tag", None)
            else:
                items.append(_item_to_nbt_entry(slot, item))
        SetBlockEntityData(network.dim, pos, data)
        # 自己写回后同样标记失效, 下次 tick 与引擎实际状态重新对齐
        _invalidate_container(network, pos)

    # print slotitem_changed


def _get_container_item(network, xyz, slot):
    # type: (CableNetwork, tuple[int, int, int], int) -> Item | None
    cache = network._cache_slotitems.get(xyz)
    if cache is None:
        cache = network._cache_slotitems[xyz] = {}
    elif slot in cache:
        return cache[slot]
    _, items = _get_container_nbt(network.dim, xyz, network._cache_datas)
    _, entry = _find_slot_entry(items, slot)
    if entry is None:
        res = None
    else:
        res = _nbt_entry_to_item(entry)
        if res.count <= 0:
            res = None
    cache[slot] = res
    return res


def _get_container_slotposes(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> tuple[tuple[int, ...], tuple[int, ...]]
    "获取容器的 (输入槽位, 输出槽位), 跨 tick 缓存到网络上"
    cached = network._cache_slotposes.get(xyz, MISSING)
    if cached is not MISSING:
        return cached
    m = GetMachineStrict(network.dim, *xyz)
    if isinstance(m, ItemContainer):
        res = (m.input_slots, m.output_slots)
    else:
        size = GetContainerSize(xyz, network.dim)
        if size is None:
            res = ((), ())
        else:
            slot_range = tuple(py2_xrange(size))
            res = (slot_range, slot_range)
    network._cache_slotposes[xyz] = res
    return res


def _get_container_input_slots(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> tuple[int, ...]
    return _get_container_slotposes(network, xyz)[0]


def _get_container_output_slots(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> tuple[int, ...]
    return _get_container_slotposes(network, xyz)[1]


def _get_block_name(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> str
    res = network._cache_block_names.get(xyz, MISSING)
    if res is MISSING:
        res = network._cache_block_names[xyz] = GetBlockName(network.dim, xyz) or ""
    return res


def _invalidate_container(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> None
    "容器内容/方块变化后使该容器的缓存失效, 下次 tick 重新读取"
    network._cache_datas.pop(xyz, None)
    network._cache_block_names.pop(xyz, None)
    network._cache_slotposes.pop(xyz, None)
    network._cache_slotitems.pop(xyz, None)


logic_module = LogicModule(
    CableNetwork,
    CableAccessPoint,
    transmitter_check_func=isCable,
    transmittable_block_check_func=isContainer,
    on_transmittable_block_placed_later=onMachineryPlacedLater,
    on_network_tick=onNetworkTick,
)


@ContainerItemChangedServerEvent.Listen()
def onContainerItemChanged(event):
    # type: (ContainerItemChangedServerEvent) -> None
    "容器内容变化时, 使连接到该容器的所有电缆网络的缓存失效"
    pos = event.pos
    if pos is None:
        return
    cnode = logic_module.container_nodes_pool.get(
        (event.dimensionId, (pos[0], pos[1], pos[2]))
    )
    if cnode is None:
        return
    for network in cnode.inputs.values():
        if network is not None:
            _invalidate_container(network, (pos[0], pos[1], pos[2]))
    for network in cnode.outputs.values():
        if network is not None:
            _invalidate_container(network, (pos[0], pos[1], pos[2]))


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)
