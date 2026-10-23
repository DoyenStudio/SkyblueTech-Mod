# coding=utf-8
"""内置管线等级注册。资源和方块标签由附属提供，配置只保存在本次会话。"""
import math

from skybluetech_scripts.tooldelta.utils.py_comp import py2_long, py2_unicode


def _modules():
    # 延迟导入：server.export 也会在内置检查器初始化期间被导入。
    from ..transmitters.item_pipe import define as item_def, logic as item_logic
    from ..transmitters.fluid_pipe import define as fluid_def, logic as fluid_logic
    from ..transmitters.wire import define as wire_def, logic as wire_logic

    return {
        "item_pipe": (item_def, item_logic.logic_module),
        "fluid_pipe": (fluid_def, fluid_logic.logic_module),
        "wire": (wire_def, wire_logic.logic_module),
    }


def _validate_id(block_id):
    if not isinstance(block_id, (str, py2_unicode)):
        raise TypeError("block_id must be a string")
    parts = block_id.split(":")
    if len(parts) != 2 or not all(parts) or any(c.isspace() for c in block_id):
        raise ValueError("block_id must use namespace:name format without whitespace")


def _positive_number(value, name, integer=False):
    types = (int, py2_long) if integer else (int, py2_long, float)
    if isinstance(value, bool) or not isinstance(value, types):
        raise TypeError(name + " must be a number" + (" (integer)" if integer else ""))
    try:
        finite = not math.isnan(value) and not math.isinf(value)
    except OverflowError:
        finite = False
    if not finite or value <= 0:
        raise ValueError(name + " must be finite and positive")


def _get_snapshot():
    return dict(
        (kind, sorted(definition.TRANSFER_SPEED_MAPPING))
        for kind, (definition, _) in _modules().items()
    )


def _register(kind, block_id, transfer_speed, capacity, predicate, replace):
    _validate_id(block_id)
    if not isinstance(replace, bool):
        raise TypeError("replace must be bool")
    _positive_number(transfer_speed, "transfer_speed", integer=kind != "fluid_pipe")
    _positive_number(transfer_speed * 5, "cycle transfer budget")
    if kind == "fluid_pipe":
        _positive_number(capacity, "capacity")
        if predicate is not None and not callable(predicate):
            raise TypeError("can_transmit_fluid must be callable or None")
        transfer_speed = float(transfer_speed)
        capacity = float(capacity)
    else:
        transfer_speed = int(transfer_speed)
    modules = _modules()
    for other_kind, (other_def, _) in modules.items():
        if other_kind != kind and block_id in other_def.TRANSFER_SPEED_MAPPING:
            raise ValueError("block_id is already registered as " + other_kind)
    definition, logic = modules[kind]
    speeds = definition.TRANSFER_SPEED_MAPPING
    exists = block_id in speeds
    same = exists and speeds[block_id] == transfer_speed
    if kind == "fluid_pipe":
        same = (
            same
            and definition.CAPACITY_MAPPING.get(block_id) == capacity
            and definition.FLUID_PIPE_CAN_TRANSMIT_FLUID_MAPPING.get(block_id) is predicate
        )
    if same:
        return
    if exists and not replace:
        raise ValueError("different configuration exists; use replace=True")

    # 完成校验后才改变配置；保持活网络及其缓冲内容，不通过拆网刷新参数。
    speeds[block_id] = transfer_speed
    if kind == "fluid_pipe":
        definition.CAPACITY_MAPPING[block_id] = capacity
        filters = definition.FLUID_PIPE_CAN_TRANSMIT_FLUID_MAPPING
        if predicate is None:
            filters.pop(block_id, None)
        else:
            filters[block_id] = predicate
    for network in tuple(logic.networks_pool):
        if network.enabled and network.transmitter_id == block_id:
            network.transfer_speed = transfer_speed * 5
            if kind == "fluid_pipe":
                network.capacity = capacity
    if not exists:
        from ...common.events.misc.transmitter_registry import TransmitterRegistrySnapshot

        TransmitterRegistrySnapshot(_get_snapshot()).sendAll()


def RegisterItemPipe(block_id, transfer_speed, replace=False):
    """注册物品管道, transfer_speed 为正整数物品数/t。"""
    _register("item_pipe", block_id, transfer_speed, None, None, replace)


def RegisterFluidPipe(
    block_id, transfer_speed, capacity, can_transmit_fluid=None, replace=False
):
    """注册流体管道: 速率 mB/t、全网容量 mB, None 过滤器表示允许所有流体。"""
    _register(
        "fluid_pipe", block_id, transfer_speed, capacity, can_transmit_fluid, replace
    )


def RegisterWire(block_id, transfer_speed, replace=False):
    """注册电缆, transfer_speed 为正整数 RF/t。"""
    _register("wire", block_id, transfer_speed, None, None, replace)



def RefreshPowerConnections(dim, x, y, z):
    """Refresh cached wire endpoints after a machine changes its RF face modes.

    Existing wire connection switches remain unchanged. Wire networks contain
    no material buffer; fluid and item networks are deliberately untouched.
    Call on structural/configuration changes, never every machine tick.
    """
    from ..transmitters.wire.logic import logic_module

    logic_module.clean_container_networks(dim, x, y, z)


__all__ = ["RegisterItemPipe", "RegisterFluidPipe", "RegisterWire", "RefreshPowerConnections"]
