# coding=utf-8

from skybluetech_scripts.tooldelta.api.server.block import BlockHasTag
from ...machinery.basic.fluid_container import FluidContainer
from ...machinery.basic.multi_fluid_container import MultiFluidContainer
from ...machinery.pool import GetMachineStrict
from ....common.define.facing import NEIGHBOR_BLOCKS_ENUM
from ..base import LogicModule
from .define import PipeNetwork, PipeAccessPoint


PIPE_NAME = "skybluetech:bronze_pipe"
INFINITY = float("inf")


def isPipe(blockName):
    # type: (str) -> bool
    return BlockHasTag(blockName, "skybluetech_pipe")


def isFluidContainer(blockName):
    return BlockHasTag(blockName, "skybluetech_fluid_container")


def PostFluidIntoNetworks(dim, xyz, fluid_id, fluid_volume, networks):
    # type: (int, tuple[int, int, int], str, float, list[PipeNetwork] | None) -> tuple[bool, float]
    """
    向网络发送流体, 返回是否添加成功和剩余流体体积


    Args:
        dim (int): 维度 ID
        xyz (tuple[int, int, int]): 坐标
        fluid_id (str): 流体 ID
        fluid_volume (float): 流体体积
        networks (list[PipeNetwork] | None): 网络列表, 为 None 则为自动获取容器周围的流体管道网络
        depth (int): 递归深度

    Returns:
        tuple[bool, float]: 是否输送出流体, 剩余体积
    """
    ok = False
    if networks is None:
        x, y, z = xyz
        networks = [
            i
            for i in logic_module.GetContainerNode(
                dim, x, y, z, enable_cache=True
            ).outputs.values()
            if i is not None
        ]
    for network in networks:
        once_transfer_vol_max = network.transfer_speed or INFINITY
        for ap in sorted(
            network.group_inputs,
            key=lambda ap: ap.get_priority(),
            reverse=True,
        ):
            if xyz == ap.target_pos:
                # 别自己给自己装东西 !
                continue
            transfer_vol = min(once_transfer_vol_max, fluid_volume)
            fluid_volume -= transfer_vol
            _ok, transfer_vol_rest = PushFluidToFluidContainer(
                ap, fluid_id, transfer_vol
            )
            fluid_volume += transfer_vol_rest
            ok = ok or _ok
            if fluid_volume <= 0:
                return ok, fluid_volume
    return ok, fluid_volume


def PushFluidToFluidContainer(ap, fluid_id, fluid_volume):
    # type: (PipeAccessPoint, str, float) -> tuple[bool, float]
    "向容器内装流体, 返回是否添加成功和剩余流体体积"
    cxyz = ap.target_pos
    m = GetMachineStrict(ap.dim, *cxyz)
    if not isinstance(m, (FluidContainer, MultiFluidContainer)):
        return False, fluid_volume
    ok, rest_fluid_volume = m.AddFluid(fluid_id, fluid_volume)
    return ok, rest_fluid_volume


def RequirePostFluid(dim, xyz):
    # type: (int, tuple[int, int, int]) -> None
    "网络内某个节点向网络请求流体。"
    x, y, z = xyz
    for ap in sorted(
        [
            i
            for network in logic_module.GetContainerNode(
                dim, x, y, z, enable_cache=True
            ).inputs.values()
            if network is not None
            for i in network.group_outputs
        ],
        key=lambda ap: ap.get_priority(),
        reverse=True,
    ):
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[ap.access_facing]
        cxyz = (ap.x + dx, ap.y + dy, ap.z + dz)
        if xyz == cxyz:
            # 别自己给自己提取 !
            continue
        m = GetMachineStrict(dim, ap.x + dx, ap.y + dy, ap.z + dz)
        if isinstance(m, (FluidContainer, MultiFluidContainer)):
            m.OnTryActivate()


def onActivateNetwork(network):
    # type: (PipeNetwork) -> None
    for ap in network.get_input_access_points():
        target_pos = ap.target_pos
        RequirePostFluid(network.dim, target_pos)


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    # 在流体容器被放置后延迟执行,
    # 用于使新设备尝试索取流体
    RequirePostFluid(dim, (x, y, z))


logic_module = LogicModule(
    PipeNetwork,
    PipeAccessPoint,
    isPipe,
    isFluidContainer,
    onMachineryPlacedLater,
    onActivateNetwork,
)
