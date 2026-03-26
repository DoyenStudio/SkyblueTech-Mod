# coding=utf-8
from collections import deque
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    BlockHasTag,
    GetBlockTags,
)
from ...machinery.pool import GetMachineStrict, GetMachineWithoutCls

from ..base import LogicModule
from .define import WireNetwork, WireAccessPoint

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
    # 在机器被放置后延迟执行,
    # 用于尝试激活网络中的其他设备, 使其向新设备尝试进行一次输出
    for network in (
        i
        for i in logic_module.GetContainerNode(dim, x, y, z).inputs.values()
        if i is not None
    ):
        for ap in network.group_outputs:
            mx, my, mz = ap.target_pos
            m = GetMachineWithoutCls(dim, mx, my, mz)
            if m is not None:
                m.OnTryActivate()


def onActivateNetwork(network):
    # type: (WireNetwork) -> None
    for ap in network.get_output_access_points():
        mx, my, mz = ap.target_pos
        m = GetMachineWithoutCls(network.dim, mx, my, mz)
        if m is not None:
            m.OnTryActivate()


def onNetworkTick(network):
    # type: (WireNetwork) -> None
    tick_capacity = network.transfer_speed
    inputs = deque(network.get_input_access_points())
    outputs = network.get_output_access_points()
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
            ok, rf_output = im.AddPower(rf_output)
            if not ok:
                inputs.popleft()
            elif rf_output == 0:
                break
        om.GivebackPower(rf_output)
        tick_capacity -= rf_output
        if tick_capacity <= 0:
            break


logic_module = LogicModule(
    WireNetwork,
    WireAccessPoint,
    isWire,
    isRFMachine,
    onMachineryPlacedLater,
    onActivateNetwork,
    on_network_tick=onNetworkTick,
    provider_check_func=isPowerProvider,
    accepter_check_func=isPowerAccepter,
)
