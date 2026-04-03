# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.api.server import (
    BlockHasTag,
    GetBlockTags,
    GetEntityDimension,
)
from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
)
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls

from ..base import LogicModule
from .define import WireNetwork, WireAccessPoint, TRANSFER_SPEED_MAPPING

# TYPE_CHECKING
if 0:
    PosData = tuple[int, int, int]  # x y z
# TYPE_CHECKING END


def isNaN(x):
    return x != x


def isWire(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_wire")


def bothCanConnect(origName, blockName):
    # type: (str, str) -> bool
    tags = GetBlockTags(blockName)
    tags2 = GetBlockTags(origName)
    if (
        "redstoneflux_connectable" not in tags
        or "redstoneflux_connectable" not in tags2
    ):
        return False
    elif isWire(blockName) and isWire(blockName):
        return origName == blockName
    return True


def isRFMachine(blockName):
    return BlockHasTag(blockName, "redstoneflux_accepter") or BlockHasTag(
        blockName, "redstoneflux_provider"
    )


def isSkyblueMachine(block_tags):
    # type: (set[str]) -> bool
    return "skybluetech_machine" in block_tags


def isPowerProvider(block_name, dim, posdata):
    # type: (str, int, tuple[int, int, int, int]) -> bool
    block_tags = GetBlockTags(block_name)
    if isSkyblueMachine(block_tags):
        m = GetMachineWithoutCls(dim, *posdata[:3])
        if m is None:
            print("[ERROR] isPowerProvider get machine failed @ {}".format(posdata[:3]))
        else:
            return m.energy_io_mode[posdata[3]] == 1
    return "redstoneflux_provider" in block_tags


def isPowerAccepter(block_name, dim, posdata):
    # type: (str, int, tuple[int, int, int, int]) -> bool
    block_tags = GetBlockTags(block_name)
    if isSkyblueMachine(block_tags):
        m = GetMachineWithoutCls(dim, *posdata[:3])
        if m is None:
            print("[ERROR] isPowerAccepter get machine failed @ {}".format(posdata[:3]))
        else:
            return m.energy_io_mode[posdata[3]] == 0
    return "redstoneflux_accepter" in block_tags


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    pass


def onNetworkTick(network):
    # type: (WireNetwork) -> None
    tick_capacity = network.transfer_speed
    inputs = deque(network.get_input_access_points())
    outputs = network.get_output_access_points()
    transfered_rf = 0
    for output in outputs:
        om = GetMachineStrict(network.dim, *output.target_pos)
        if om is None:
            continue
        rf_output = om.TakeoutPower(tick_capacity)
        if rf_output <= 0:
            continue
        while inputs:
            input = inputs[0]
            im = GetMachineStrict(network.dim, *input.target_pos)
            if im is None:
                inputs.popleft()
                continue
            ok, rf_rest = im.AddPower(rf_output)
            transfered_rf += rf_output - rf_rest
            rf_output = rf_rest
            if not ok:
                inputs.popleft()
            elif rf_output == 0:
                break
        om.GivebackPower(rf_output)
        tick_capacity -= rf_output
        if tick_capacity <= 0:
            break
    network.trigger_shock(transfered_rf)


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
    dim = GetEntityDimension(event.entityId)
    network = logic_module.GetNetworkByTransmitter(
        dim, event.blockX, event.blockY, event.blockZ, force_use_cached=True
    )
    if network is not None:
        network.entities_hit_wire[event.entityId] = (
            event.blockX,
            event.blockY,
            event.blockZ,
        )
