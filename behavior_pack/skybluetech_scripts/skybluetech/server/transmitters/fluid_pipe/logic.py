# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID


from ...machinery.basic.multi_fluid_container import MultiFluidContainer
from ...machinery.core.pool import GetLoadedMachine
from ..base import LogicModule
from .define import FluidPipeNetwork, FluidPipeAccessPoint, FLUID_PIPE_CAN_TRANSMIT_FLUID_MAPPING

_block_tags_cache = {}  # type: dict[str, set[str]]


def is_fluid_pipe(blockName):
    # type: (str) -> bool
    tags = _block_tags_cache.get(blockName)
    if tags is None:
        tags = _block_tags_cache[blockName] = set(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(blockName)
        )
    return "skybluetech_fluid_pipe" in tags


def isFluidContainer(blockName, dim=None, xyz=None):
    # type: (str, int | None, tuple[int, int, int] | None) -> bool
    tags = _block_tags_cache.get(blockName)
    if tags is None:
        tags = _block_tags_cache[blockName] = set(
            CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(blockName)
        )
    return "skybluetech_fluid_container" in tags


def PostFluidIntoNetworks(dim, xyz, fluid_id, fluid_volume, networks):
    # type: (int, tuple[int, int, int], str, float, list[FluidPipeNetwork] | None) -> tuple[bool, float]
    """
    向网络发送流体, 返回是否添加成功和剩余流体体积


    Args:
        dim (int): 维度 ID
        xyz (tuple[int, int, int]): 坐标
        fluid_id (str): 流体 ID
        fluid_volume (float): 流体体积
        networks (list[FluidPipeNetwork] | None): 网络列表, 为 None 则为自动获取容器周围的流体管道网络
        depth (int): 递归深度

    Returns:
        tuple[bool, float]: 是否输送出流体, 剩余体积
    """
    if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
        return False, fluid_volume
    ok = False
    if networks is None:
        x, y, z = xyz
        networks = list(
            logic_module
            .GetContainerNode(dim, x, y, z, enable_cache=True)
            .get_outputs()
            .values()
        )
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
    # type: (FluidPipeAccessPoint, str, float) -> tuple[bool, float]
    "向容器内装流体, 返回是否添加成功和剩余流体体积"
    if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
        return False, fluid_volume
    cxyz = ap.target_pos
    m = GetLoadedMachine(ap.dim, *cxyz)
    if not isinstance(m, MultiFluidContainer):
        return False, fluid_volume
    if m.fluid_input_slots_by_face is None:
        ok, rest_fluid_volume = m.AddFluid(fluid_id, fluid_volume)
    else:
        relative_face = m.GetRelativeFacingFromAccessFacing(ap.access_facing)
        ok, rest_fluid_volume = m.AddFluidFromFace(
            fluid_id, fluid_volume, relative_face
        )
    return ok, rest_fluid_volume


def onMachineryPlacedLater(dim, x, y, z):
    # type: (int, int, int, int) -> None
    # 在流体容器被放置后延迟执行,
    # 用于使新设备尝试索取流体
    pass


def onNetworkTick(network):
    # type: (FluidPipeNetwork) -> None
    transfer_speed = network.transfer_speed
    fluid_pipe_fluid_id = network.fluid_id
    fluid_pipe_fluid_volume = network.fluid_volume
    capacity = network.capacity
    if fluid_pipe_fluid_id is None or fluid_pipe_fluid_volume <= 0:
        fluid_pipe_fluid_id = None
        fluid_pipe_fluid_volume = 0.0
    if fluid_pipe_fluid_id is not None and fluid_pipe_fluid_volume > 0:
        volume_output = min(transfer_speed, fluid_pipe_fluid_volume)
        fluid_pipe_fluid_volume -= volume_output
        for input in network.get_input_access_points():
            ok, volume_output = PushFluidToFluidContainer(
                input, fluid_pipe_fluid_id, volume_output
            )
            if volume_output <= 0:
                break
        fluid_pipe_fluid_volume += volume_output
    out_capacity = max(0, min(transfer_speed, capacity - fluid_pipe_fluid_volume))
    for output in network.get_output_access_points():
        if out_capacity <= 0:
            break
        om = GetLoadedMachine(output.dim, *output.target_pos)
        if isinstance(om, MultiFluidContainer):
            do_break = False
            relative_face = None
            if om.fluid_output_slots_by_face is not None:
                relative_face = om.GetRelativeFacingFromAccessFacing(output.access_facing)
            for slot in om.GetFluidOutputSlotsForFace(relative_face):
                fluid = om.fluids[slot]
                fluid_id = fluid.fluid_id
                if fluid_id is not None and fluid.volume <= 0:
                    fluid.volume = 0.0
                    fluid_id = None
                if (
                    fluid_id is None
                    or (fluid_pipe_fluid_id is not None and fluid_id != fluid_pipe_fluid_id)
                    or not fluid_pipe_can_transfer_fluid(network.transmitter_id, fluid_id)
                    or fluid.volume <= 0
                ):
                    continue
                vol_takeout = min(out_capacity, fluid.volume)
                fluid.volume -= vol_takeout
                if fluid.volume <= 0:
                    fluid.fluid_id = None
                fluid_pipe_fluid_volume += vol_takeout
                out_capacity -= vol_takeout
                if fluid_pipe_fluid_id is None:
                    fluid_pipe_fluid_id = fluid_id
                om._on_reduced_fluid(
                    slot, fluid_id, vol_takeout, is_final=True
                )  # 每次扣液作为一次完整的槽位操作通知。
                if out_capacity <= 0:
                    do_break = True
                    break
            if do_break:
                break
    network.fluid_volume = fluid_pipe_fluid_volume
    if fluid_pipe_fluid_volume <= 0:
        network.fluid_id = None
    else:
        network.fluid_id = fluid_pipe_fluid_id
    network.save_network_data()


def fluid_pipe_can_transfer_fluid(fluid_pipe_id, fluid_id):
    # type: (str, str) -> bool
    return FLUID_PIPE_CAN_TRANSMIT_FLUID_MAPPING.get(fluid_pipe_id, lambda _: True)(fluid_id)


logic_module = LogicModule(
    FluidPipeNetwork,
    FluidPipeAccessPoint,
    transmitter_check_func=is_fluid_pipe,
    on_transmittable_block_placed_later=onMachineryPlacedLater,
    transmittable_block_check_func=isFluidContainer,
    on_network_tick=onNetworkTick,
)
