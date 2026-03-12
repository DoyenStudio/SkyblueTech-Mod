# coding=utf-8

from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockName,
    BlockHasTag,
    GetBlockTags,
)
from ...machinery.basic import BaseMachine
from ...machinery.pool import GetMachineStrict, GetMachineCls, GetMachineWithoutCls

from ..base import LogicModule
from .define import WireNetwork, WireAccessPoint

# TYPE_CHECKING
if 0:
    PosData = tuple[int, int, int]  # x y z
# TYPE_CHECKING END


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
        _block_name = GetBlockName(dim, posdata[:3])
        if _block_name is None:
            return False
        return GetMachineCls(_block_name).energy_io_mode[posdata[3]] == 1
    return "redstoneflux_provider" in block_tags


def isPowerAccepter(block_name, dim, posdata):
    # type: (str, int, tuple[int, int, int, int]) -> bool
    block_tags = GetBlockTags(block_name)
    if isSkyblueMachine(block_tags):
        _block_name = GetBlockName(dim, posdata[:3])
        if _block_name is None:
            return False
        return GetMachineCls(_block_name).energy_io_mode[posdata[3]] == 0
    return "redstoneflux_accepter" in block_tags


def RequireEnergyFromNetwork(machine):
    # type: (BaseMachine) -> bool
    ok = False
    networks = (
        i
        for i in logic_module.GetContainerNode(
            machine.dim, machine.x, machine.y, machine.z
        ).outputs.values()
        if i is not None
    )
    for network in networks:
        if network is None:
            continue
        generator_nodes = network.get_output_access_points()
        for ap in generator_nodes:
            m2 = GetMachineStrict(machine.dim, *ap.target_pos)
            if m2 is None:
                continue
            m2.OnTryActivate()  # 这样尝试输出能源
            ok = True
    return ok


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


logic_module = LogicModule(
    WireNetwork,
    WireAccessPoint,
    isWire,
    isRFMachine,
    onMachineryPlacedLater,
    onActivateNetwork,
    provider_check_func=isPowerProvider,
    accepter_check_func=isPowerAccepter,
)
