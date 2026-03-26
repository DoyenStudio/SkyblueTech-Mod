# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ....common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
    RFRepeaterPlantBuildAddWire,
    RFRepeaterPlantSettingUpload,
)
from ....common.machinery_def.rf_repeater_plant import MODE_INPUT, MODE_OUTPUT
from ..pool import GetMachineStrict
from .node import change_node_mode, build_connection
from .utils import hypot

build_speed_limiter = PlayerRateLimiter(1)


@RFRepeaterPlantBuildRequest.Listen()
def onEstablishConn(event):
    # type: (RFRepeaterPlantBuildRequest) -> None
    from . import RFRepeaterPlant
    from .core import block_sync

    if not build_speed_limiter.record(event.player_id):
        RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_TOO_FAST).send(
            event.player_id
        )
        return
    dim = GetPlayerDimensionId(event.player_id)
    start_m = GetMachineStrict(dim, event.x, event.y, event.z)
    if not isinstance(start_m, RFRepeaterPlant) or not start_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_START
        ).send(event.player_id)
        return
    end_m = GetMachineStrict(dim, event.to_x, event.to_y, event.to_z)
    if not isinstance(end_m, RFRepeaterPlant) or not end_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_END
        ).send(event.player_id)
        return
    start_pos = (event.x, event.y, event.z)
    end_pos = (event.to_x, event.to_y, event.to_z)
    start_nearby_nodes = start_m.get_nearconn_plants()
    end_nearby_nodes = end_m.get_nearconn_plants()
    if start_nearby_nodes is None or end_nearby_nodes is None:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR
        ).send(event.player_id)
        return
    elif start_pos in end_nearby_nodes or end_pos in start_nearby_nodes:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_ALREADY_CONNECTED
        ).send(event.player_id)
        return
    elif start_pos == end_pos:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_CANT_CONNECT_SELF
        ).send(event.player_id)
        return
    if (
        hypot(
            start_pos[0] - end_pos[0],
            start_pos[1] - end_pos[1],
            start_pos[2] - end_pos[2],
        )
        > 64
    ):
        RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_TOO_FAR).send(
            event.player_id
        )
        return
    res = build_connection(dim, start_pos, end_pos)
    if not res:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR2
        ).send(event.player_id)
        return
    RFRepeaterPlantBuildResponse(RFRepeaterPlantBuildResponse.STATUS_SUCC).send(
        event.player_id
    )
    RFRepeaterPlantBuildAddWire(
        event.x, event.y, event.z, event.to_x, event.to_y, event.to_z
    ).sendMulti(block_sync.get_players((dim,) + start_pos))


@RFRepeaterPlantSettingUpload.Listen()
def onSettingUpload(event):
    # type: (RFRepeaterPlantSettingUpload) -> None
    from . import RFRepeaterPlant

    dim = GetPlayerDimensionId(event.player_id)
    m = GetMachineStrict(dim, event.x, event.y, event.z)
    if not isinstance(m, RFRepeaterPlant):
        return
    if not m.is_base_block:
        return
    if event.io_mode not in {MODE_INPUT, MODE_OUTPUT}:
        return
    change_node_mode(dim, event.x, event.y, event.z, event.io_mode)
