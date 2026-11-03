# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from collections import deque

from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
)
from ...export import energy
from ...machinery.core.pool import GetMachineWithoutCls
from ....common.define.facing import OPPOSITE_FACING

from ..base import LogicModule
from .define import WireNetwork, WireAccessPoint, TRANSFER_SPEED_MAPPING

# TYPE_CHECKING
if 0>1:
    import typing

    PosData = typing.Tuple[int, int, int]  # x y z
# TYPE_CHECKING END

_block_tags_cache = {}  # type: dict[str, set[str]]


def isNaN(x):
    return x != x


def isWire(blockName):
    # type: (str) -> bool
    tags = _block_tags_cache.get(blockName)
    if tags is None:
        tags = _block_tags_cache[blockName] = set(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(blockName)
        )
    return "skybluetech_wire" in tags


def isRFMachine(blockName, dim=None, xyz=None):
    # type: (str, int | None, tuple[int, int, int] | None) -> bool
    tags = _block_tags_cache.get(blockName)
    if tags is None:
        tags = _block_tags_cache[blockName] = set(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(blockName)
        )
    return (energy.IsExternalEnergyBlock(blockName) or
            "redstoneflux_accepter" in tags or "redstoneflux_provider" in tags)


def isSkyblueMachine(block_tags):
    # type: (set[str]) -> bool
    return "skybluetech_machine" in block_tags


def _allowsPower(block_name, dim, posdata, mode):
    if energy.IsExternalEnergyBlock(block_name):
        handler = energy.GetEnergyHandler(posdata[:3], dim, posdata[3])
        return handler is not None and (handler.canExtract() if mode == 1 else handler.canReceive())
    tags = _block_tags_cache.get(block_name)
    if tags is None:
        tags = _block_tags_cache[block_name] = set(CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(block_name))
    if isSkyblueMachine(tags):
        machine = GetMachineWithoutCls(dim, *posdata[:3])
        return machine is not None and machine.energy_io_mode[posdata[3]] == mode
    return ("redstoneflux_provider" if mode == 1 else "redstoneflux_accepter") in tags


def isPowerProvider(block_name, dim, posdata):
    return _allowsPower(block_name, dim, posdata, 1)


def isPowerAccepter(block_name, dim, posdata):
    return _allowsPower(block_name, dim, posdata, 0)


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    pass


def onNetworkTick(network):
    # type: (WireNetwork) -> None
    tick_capacity = network.transfer_speed
    inputs = tuple(network.get_input_access_points())
    outputs = network.get_output_access_points()
    transfered_rf = 0
    for output in outputs:
        source = energy.GetEnergyHandler(output.target_pos, network.dim, OPPOSITE_FACING[output.access_facing])
        if source is None or not source.canExtract():
            continue
        ticket = source.prepareExtract(int(tick_capacity))
        if ticket is None:
            continue
        remaining = ticket.amount
        candidates = deque(inputs)
        try:
            while candidates and remaining:
                access = candidates[0]
                if access.target_pos == output.target_pos:
                    candidates.popleft()
                    continue
                target = energy.GetEnergyHandler(access.target_pos, network.dim, OPPOSITE_FACING[access.access_facing])
                if target is None or not target.canReceive():
                    candidates.popleft()
                    continue
                if energy.SameEnergyStorage(source, target):
                    candidates.popleft()
                    continue
                accepted = energy._quantity(target.insert(remaining))
                if accepted > remaining:
                    raise RuntimeError("energy receiver exceeded offer")
                remaining -= accepted
                if remaining:
                    candidates.popleft()
        except Exception:
            # 对端可能已入账，结果不明时不能退款再次发放。
            ticket.finish(ticket.amount)
            raise
        ticket.finish(ticket.amount - remaining)
        moved = ticket.amount - remaining
        transfered_rf += moved
        tick_capacity -= moved
        if tick_capacity <= 0:
            break
    network.trigger_shock(transfered_rf)
    network.power_through_sum += transfered_rf
    network.run_ticks += 1
    if network.run_ticks >= 4:
        network.run_ticks = 0
        network.power_through_avg = network.power_through_sum / 4.0
        network.power_through_sum = 0.0


logic_module = LogicModule(
    WireNetwork,
    WireAccessPoint,
    transmitter_check_func=isWire,
    transmittable_block_check_func=isRFMachine,
    on_transmittable_block_placed_later=onMachineryPlacedLater,
    on_network_tick=onNetworkTick,
    provider_check_func=isPowerProvider,
    accepter_check_func=isPowerAccepter,
)


@OnEntityInsideBlockServerEvent.Listen()
def onEntityInsideBlock(event):
    # type: (OnEntityInsideBlockServerEvent) -> None
    if event.blockName not in TRANSFER_SPEED_MAPPING:
        return
    dim = CF.CreateDimension(event.entityId).GetEntityDimensionId()
    network = logic_module.GetNetworkByTransmitter(
        dim, event.blockX, event.blockY, event.blockZ, force_use_cached=True
    )
    if network is not None:
        network.entities_hit_wire[event.entityId] = (
            event.blockX,
            event.blockY,
            event.blockZ,
        )
