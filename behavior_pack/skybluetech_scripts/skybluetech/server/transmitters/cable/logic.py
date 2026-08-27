# coding=utf-8

from skybluetech_scripts.tooldelta.api.server import (
    BlockHasTag,
    GetBlockName,
    GetContainerItem,
    GetContainerSize,
    SetBlockEntityData,
    SetContainerItem,
)
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ContainerItemChangedServerEvent,
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
from ..constants import CHEST_CONTAINERS, COMMON_CONTAINERS
from .define import CableAccessPoint, CableNetwork
from .nbt_utils import (
    MISSING,
    _find_slot_entry,
    _get_container_nbt,
    _item_to_nbt_entry,
    _nbt_entry_to_item,
)

# TYPE_CHECKING
if 0 > 1:
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
            logic_module
            .GetContainerNode(dim, x, y, z, enable_cache=True)
            .get_outputs()
            .values()
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
    # 大箱子两个半箱经容器 API 暴露同一份 0-53 全局槽位, 同一 tick 内
    # 每个大箱子只允许一个输出端/输入端参与, 否则同一批物品会被重复搬移
    scanned_out_chest_pairs = set()  # type: set[tuple[tuple[int, int, int], tuple[int, int, int]]]
    scanned_in_chest_pairs = set()  # type: set[tuple[tuple[int, int, int], tuple[int, int, int]]]
    for output_index in range(output_count):
        output_ap = outputs[(start + output_index) % output_count]
        output_pos = output_ap.target_pos
        output_slotposes = _get_container_output_slots(network, output_pos)

        pair_pos = None
        if _is_chest(network, output_pos):
            pair_data, _ = _get_container_nbt(
                network.dim, output_pos, network._cache_datas
            )
            pair_x = GetValueWithDefault(pair_data or {}, "pairx", None)
            pair_z = GetValueWithDefault(pair_data or {}, "pairz", None)
            pair_y = output_pos[1]
            if pair_x is not None and pair_z is not None:
                pair_pos = (pair_x, pair_y, pair_z)
        else:
            pair_x = pair_z = pair_y = None

        if pair_pos is not None:
            pair_key = (min(output_pos, pair_pos), max(output_pos, pair_pos))
            if pair_key in scanned_out_chest_pairs:
                continue
            scanned_out_chest_pairs.add(pair_key)

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
                    _is_chest(network, input_pos)
                    and pair_x == input_pos[0]
                    and pair_z == input_pos[2]
                    and pair_y == input_pos[1]
                ):
                    # 跳过双箱子的另一半, 避免同一容器互相搬运
                    continue

                # 输入端同一 tick 也只允许大箱子的一个半箱参与投递
                if _is_chest(network, input_pos):
                    ipair_data, _ = _get_container_nbt(
                        network.dim, input_pos, network._cache_datas
                    )
                    ipair_x = GetValueWithDefault(ipair_data or {}, "pairx", None)
                    ipair_z = GetValueWithDefault(ipair_data or {}, "pairz", None)
                    if ipair_x is not None and ipair_z is not None:
                        ipair_pos = (ipair_x, input_pos[1], ipair_z)
                        ipair_key = (
                            min(input_pos, ipair_pos),
                            max(input_pos, ipair_pos),
                        )
                        if ipair_key in scanned_in_chest_pairs:
                            continue
                        scanned_in_chest_pairs.add(ipair_key)

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

    # 先收集本次 tick 所有待写回槽位: SetContainerItem 会同步触发容器变化
    # 事件并使缓存失效, 若边写边读缓存, 配对半箱的写回会被"缓存中途失效"
    # 逻辑丢弃, 导致源箱扣减少于目标增加 (刷物)
    pending_writes = {}  # type: dict[tuple[int, int, int], list[tuple[int, Item | None]]]
    for pos, changed_slots in slotitem_changed.items():
        slotitems = network._cache_slotitems.get(pos)
        if slotitems is None:
            # 缓存中途被外部事件失效, 放弃本次写回, 下次 tick 重新读取
            continue
        writes = []
        for slot in changed_slots:
            item = slotitems.get(slot, MISSING)
            if item is MISSING:
                continue
            writes.append((slot, item))
        if writes:
            pending_writes[pos] = writes

    for pos, writes in pending_writes.items():
        if _is_chest(network, pos):
            # 箱子/陷阱箱使用容器 API 读写: 大箱子两个方块实体各自只存
            # 本地 0-26 槽, 而容器 API 把两个半箱映射成统一的 0-53 槽位
            for slot, item in writes:
                if item is None:
                    SetContainerItem(network.dim, pos, slot, Item("minecraft:air"))
                else:
                    SetContainerItem(network.dim, pos, slot, item)
            _invalidate_container(network, pos)
            continue
        data, items = _get_container_nbt(network.dim, pos, network._cache_datas)
        if data is None:
            continue
        for slot, item in writes:
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


def _get_container_item(network, xyz, slot):
    # type: (CableNetwork, tuple[int, int, int], int) -> Item | None
    cache = network._cache_slotitems.get(xyz)
    if cache is None:
        cache = network._cache_slotitems[xyz] = {}
    elif slot in cache:
        return cache[slot]
    if _is_chest(network, xyz):
        res = GetContainerItem(network.dim, xyz, slot, getUserData=True)
        if res is None or res.count <= 0:
            res = None
        cache[slot] = res
        return res
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


def _is_chest(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> bool
    "箱子、陷阱箱和铜箱子变种可组成大箱子, 每半的方块实体 NBT 只含本地 0-26 槽, 需走容器 API"
    return _get_block_name(network, xyz) in CHEST_CONTAINERS


def _invalidate_container(network, xyz):
    # type: (CableNetwork, tuple[int, int, int]) -> None
    "容器内容/方块变化后使该容器的缓存失效, 下次 tick 重新读取"
    network._cache_datas.pop(xyz, None)
    network._cache_block_names.pop(xyz, None)
    network._cache_slotposes.pop(xyz, None)
    network._cache_slotitems.pop(xyz, None)
    # 大箱子两个半箱共享同一个容器视图, 内容变化时同步失效另一半的缓存
    if _is_chest(network, xyz):
        data, _ = _get_container_nbt(network.dim, xyz, network._cache_datas)
        pair_x = GetValueWithDefault(data or {}, "pairx", None)
        pair_z = GetValueWithDefault(data or {}, "pairz", None)
        if pair_x is not None and pair_z is not None:
            pair_pos = (pair_x, xyz[1], pair_z)
            if pair_pos != xyz:
                network._cache_datas.pop(pair_pos, None)
                network._cache_block_names.pop(pair_pos, None)
                network._cache_slotposes.pop(pair_pos, None)
                network._cache_slotitems.pop(pair_pos, None)


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
    dim = event.dimensionId
    # 大箱子: 物品变化事件只携带实际发生变化的半箱坐标, 而管道可能只连接了
    # 另一个半箱。若事件半箱不在连接池中, 沿 pairx/pairz 找到配对半箱, 让连接
    # 在配对半箱上的网络缓存一并失效, 否则另一侧半箱的物品永远读不到。
    positions = [pos]
    if GetBlockName(dim, pos) in CHEST_CONTAINERS:
        data, _ = _get_container_nbt(dim, pos, {})
        pair_x = GetValueWithDefault(data or {}, "pairx", None)
        pair_z = GetValueWithDefault(data or {}, "pairz", None)
        if pair_x is not None and pair_z is not None:
            pair_pos = (pair_x, pos[1], pair_z)
            if pair_pos != pos:
                positions.append(pair_pos)
    invalidated_networks = set()  # type: set[CableNetwork]
    for p in positions:
        cnode = logic_module.container_nodes_pool.get((dim, (p[0], p[1], p[2])))
        if cnode is None:
            continue
        for network in cnode.inputs.values():
            if network is not None and network not in invalidated_networks:
                _invalidate_container(network, p)
                invalidated_networks.add(network)
        for network in cnode.outputs.values():
            if network is not None and network not in invalidated_networks:
                _invalidate_container(network, p)
                invalidated_networks.add(network)


BlockRemoveServerEvent.AddExtraBlocks(COMMON_CONTAINERS)
