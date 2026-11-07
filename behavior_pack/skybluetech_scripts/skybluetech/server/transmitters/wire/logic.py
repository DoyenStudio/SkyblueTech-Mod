# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from itertools import groupby

from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
)
from ...export import energy
from ... import transferlib
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
        if handler is not None and (handler.canExtract() if mode == 1 else handler.canReceive()):
            return True
        return transferlib.has_port("radium:energy", dim, posdata[:3], posdata[3])
    tags = _block_tags_cache.get(block_name)
    if tags is None:
        tags = _block_tags_cache[block_name] = set(CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(block_name))
    if isSkyblueMachine(tags):
        machine = GetMachineWithoutCls(dim, *posdata[:3])
        return machine is not None and machine.energy_io_mode[posdata[3]] == mode
    if ("redstoneflux_provider" if mode == 1 else "redstoneflux_accepter") in tags:
        return True
    return transferlib.has_port("radium:energy", dim, posdata[:3], posdata[3])


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
        try:
            moved = transfer_from_port(output, inputs, int(tick_capacity))
        except Exception as exc:
            if transferlib.api is None or not isinstance(exc, transferlib.api.TransactionError):
                raise
            continue
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


def distribute_legacy(source, targets, budget):
    if source is None or not source.canExtract():
        return 0
    ticket = source.prepareExtract(budget)
    if ticket is None:
        return 0
    remaining = ticket.amount
    try:
        for target in targets:
            if not target.canReceive() or energy.SameEnergyStorage(source, target):
                continue
            accepted = energy._quantity(target.insert(remaining))
            if accepted > remaining:
                raise RuntimeError("energy receiver exceeded offer")
            remaining -= accepted
            if not remaining:
                break
    except Exception:
        ticket.finish(ticket.amount)
        raise
    moved = ticket.amount - remaining
    ticket.finish(moved)
    return moved


def transfer_from_port(output, inputs, budget):
    api = transferlib.api
    native = energy.GetEnergyHandler(output.target_pos, output.dim, OPPOSITE_FACING[output.access_facing])
    source = transferlib.at_access(api.ENERGY, output) if api is not None else None
    if source is None and native is None:
        return 0

    def targets():
        for access in inputs:
            if access.target_pos == output.target_pos:
                continue
            if source is not None:
                target = transferlib.at_access(api.ENERGY, access)
                if target is not None:
                    yield True, target
                    continue
            if native is not None:
                target = energy.GetEnergyHandler(access.target_pos, access.dim, OPPOSITE_FACING[access.access_facing])
                if target is not None:
                    yield False, target

    remaining = budget
    if source is not None:
        # Keep the source limit across protocol groups, including legacy-only targets.
        try:
            with api.open_transaction() as probe:
                remaining = source.extract(budget, probe)
        except api.TransactionError:
            return 0
    available = remaining
    # Resolve endpoints before the first commit, so a lookup failure has no partial effects.
    for transactional, group in groupby(list(targets()), lambda pair: pair[0]):
        if not remaining:
            break
        endpoints = [target for _, target in group]
        if transactional:
            try:
                with api.open_transaction() as tx:
                    moved = api.distribute_energy(source, endpoints, remaining, tx)
                    tx.commit()
            except api.TransactionError:
                break
        else:
            moved = distribute_legacy(native, endpoints, remaining)
        remaining -= moved
    return available - remaining


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


logic_module.transfer_capability = "radium:energy"


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
