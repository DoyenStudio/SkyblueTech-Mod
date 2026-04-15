# coding=utf-8

from skybluetech_scripts.tooldelta.api.server.block import BlockHasTag
from ...machinery.basic.fluid_container import FluidContainer
from ...machinery.basic.multi_fluid_container import MultiFluidContainer
from ...machinery.pool import GetMachineStrict
from ..base import LogicModule
from .define import PipeNetwork, PipeAccessPoint, PIPE_CAN_TRANSMIT_FLUID_MAPPING


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
        once_transfer_vol_max = network.transfer_speed
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


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    # 在流体容器被放置后延迟执行,
    # 用于使新设备尝试索取流体
    pass


def onNetworkTick(network):
    # type: (PipeNetwork) -> None
    transfer_speed = network.transfer_speed
    pipe_fluid_id = network.fluid_id
    pipe_fluid_volume = network.fluid_volume
    capacity = network.capacity
    if pipe_fluid_id is not None and pipe_fluid_volume > 0:
        volume_output = min(transfer_speed, pipe_fluid_volume)
        pipe_fluid_volume -= volume_output
        for input in network.get_input_access_points():
            ok, volume_output = PushFluidToFluidContainer(
                input, pipe_fluid_id, volume_output
            )
            if volume_output <= 0:
                break
        pipe_fluid_volume += volume_output
    out_capacity = min(transfer_speed, capacity - pipe_fluid_volume)
    for output in network.get_output_access_points():
        om = GetMachineStrict(output.dim, *output.target_pos)
        if isinstance(om, FluidContainer):
            om_fluid_id = om.fluid_id
            om_fluid_vol = om.fluid_volume
            if (
                om_fluid_id is None
                or (pipe_fluid_id is not None and om_fluid_id != pipe_fluid_id)
                or not pipe_can_transfer_fluid(network.transmitter_id, om_fluid_id)
            ):
                continue
            vol_takeout = min(out_capacity, om_fluid_vol)
            om_fluid_vol -= vol_takeout
            om.fluid_volume = om_fluid_vol
            if om_fluid_vol <= 0:
                om.fluid_id = None
            om.onReducedFluid(om_fluid_id, vol_takeout)
            pipe_fluid_volume += vol_takeout
            out_capacity -= vol_takeout
            if pipe_fluid_id is None:
                pipe_fluid_id = om_fluid_id
            if out_capacity <= 0:
                break
        elif isinstance(om, MultiFluidContainer):
            do_break = False
            for slot in om.fluid_output_slots:
                fluid = om.fluids[slot]
                fluid_id = fluid.fluid_id
                if (
                    fluid_id is None
                    or (pipe_fluid_id is not None and fluid_id != pipe_fluid_id)
                    or fluid.volume <= 0
                ):
                    continue
                vol_takeout = min(out_capacity, fluid.volume)
                fluid.volume -= vol_takeout
                pipe_fluid_volume += vol_takeout
                out_capacity -= vol_takeout
                if pipe_fluid_id is None:
                    pipe_fluid_id = fluid.fluid_id
                om.onReducedFluid(
                    slot, fluid_id, vol_takeout, is_final=True
                )  # TODO: fix is_final
                if out_capacity <= 0:
                    do_break = True
                    break
            if do_break:
                break
    network.fluid_volume = pipe_fluid_volume
    if pipe_fluid_volume <= 0:
        network.fluid_id = None
    else:
        network.fluid_id = pipe_fluid_id
    network.save_network_data()


def pipe_can_transfer_fluid(pipe_id, fluid_id):
    # type: (str, str) -> bool
    return PIPE_CAN_TRANSMIT_FLUID_MAPPING.get(pipe_id, lambda _: True)(fluid_id)


logic_module = LogicModule(
    PipeNetwork,
    PipeAccessPoint,
    transmitter_check_func=isPipe,
    on_transmittable_block_placed_later=onMachineryPlacedLater,
    transmittable_block_check_func=isFluidContainer,
    on_network_tick=onNetworkTick,
)
