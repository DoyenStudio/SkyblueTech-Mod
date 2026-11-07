# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID


from ... import transferlib
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
        if not fluid_pipe_can_transfer_fluid(network.transmitter_id, fluid_id):
            continue
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
            once_transfer_vol_max -= transfer_vol - transfer_vol_rest
            ok = ok or _ok
            if fluid_volume <= 0:
                return ok, fluid_volume
            if once_transfer_vol_max <= 0:
                break
    return ok, fluid_volume


def PushFluidToFluidContainer(ap, fluid_id, fluid_volume):
    # type: (FluidPipeAccessPoint, str, float) -> tuple[bool, float]
    "向容器内装流体, 返回是否添加成功和剩余流体体积"
    if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
        return False, fluid_volume
    cxyz = ap.target_pos
    m = GetLoadedMachine(ap.dim, *cxyz)
    if not isinstance(m, MultiFluidContainer):
        api = transferlib.api
        if api is not None:
            try:
                target = transferlib.at_access(api.FLUID, ap)
                if target is not None and transferlib.plain(fluid_id):
                    with api.open_transaction() as tx:
                        moved = target.insert(fluid_id, fluid_volume, tx)
                        tx.commit()
                    return moved > 0, fluid_volume - moved
            except api.TransactionError:
                pass
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


def buffer_port(network):
    if not hasattr(network, "_radium_buffer"):
        api = transferlib.api

        def apply(state):
            network.fluid_id, network.fluid_volume = state

        cell = api.create_cell((None, 0.0), read=lambda: (network.fluid_id, network.fluid_volume),
                               apply=apply, persist=network.save_network_data,
                               valid=lambda: network in logic_module.networks_pool)
        network._radium_buffer = api.create_fluid_handler(
            {0: cell}, lambda _: network.capacity,
            accepts=lambda _, r: transferlib.plain(r) and fluid_pipe_can_transfer_fluid(network.transmitter_id, r))
    return network._radium_buffer


def transfer_external(network, access, budget, pulling):
    api = transferlib.api
    if api is None:
        return 0.0
    try:
        endpoint = transferlib.at_access(api.FLUID, access)
        if endpoint is None:
            return 0.0
        buffer = buffer_port(network)
        with api.open_transaction() as tx:
            if pulling:
                moved = 0.0
                for slot in endpoint.get_slots():
                    resource = endpoint.get_resource(slot, tx)
                    if not transferlib.plain(resource):
                        continue
                    # Bulk extraction can span all slots containing this exact identity.
                    moved = api.move_fluid(endpoint, buffer, resource, budget, tx)
                    if moved:
                        break
            else:
                moved = api.move_fluid(buffer, endpoint, network.fluid_id, budget, tx)
            tx.commit()
        return moved
    except api.TransactionError:
        return 0.0


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
        # Keep the network fields current for transactional external endpoints.
        for input in network.get_input_access_points():
            if not isinstance(GetLoadedMachine(input.dim, *input.target_pos), MultiFluidContainer):
                moved = transfer_external(network, input, volume_output, False)
                volume_output -= moved
            else:
                _, rest = PushFluidToFluidContainer(input, fluid_pipe_fluid_id, volume_output)
                network.fluid_volume -= volume_output - rest
                volume_output = rest
            if volume_output <= 0:
                break
        fluid_pipe_fluid_volume = network.fluid_volume
        if not fluid_pipe_fluid_volume:
            fluid_pipe_fluid_id = network.fluid_id = None
    out_capacity = max(0, min(transfer_speed, capacity - fluid_pipe_fluid_volume))
    for output in network.get_output_access_points():
        if out_capacity <= 0:
            break
        om = GetLoadedMachine(output.dim, *output.target_pos)
        if not isinstance(om, MultiFluidContainer):
            network.fluid_id, network.fluid_volume = fluid_pipe_fluid_id, fluid_pipe_fluid_volume
            out_capacity -= transfer_external(network, output, out_capacity, True)
            fluid_pipe_fluid_id, fluid_pipe_fluid_volume = network.fluid_id, network.fluid_volume
        else:
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
logic_module.transfer_capability = "radium:fluid"
