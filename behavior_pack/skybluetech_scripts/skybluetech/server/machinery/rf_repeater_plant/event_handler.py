# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF
from mod_log import logger

from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.skybluetech.common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
    RFRepeaterPlantBuildAddWire,
    RFRepeaterPlantSettingUpload,
)
from skybluetech_scripts.skybluetech.common.machinery_def.rf_repeater_plant import (
    MODE_INPUT,
    MODE_OUTPUT,
)
from ..core.pool import GetLoadedMachine
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
    dim = CF.CreateDimension(event.player_id).GetEntityDimensionId()
    start_m = GetLoadedMachine(dim, event.x, event.y, event.z)
    if not isinstance(start_m, RFRepeaterPlant):
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_START, sub_status_code=0
        ).send(event.player_id)
        logger.warning(
            "[SkyblueTech] RFRepeaterPlant: player built invalid end plant at {}: {}".format(
                (event.to_x, event.to_y, event.to_z), start_m
            )
        )
        return
    elif not start_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_START, sub_status_code=1
        ).send(event.player_id)
        logger.warning(
            "[SkyblueTech] RFRepeaterPlant: player built invalid start plant layer at {}: {}".format(
                (event.x, event.y, event.z), start_m.layer
            )
        )
        return
    end_m = GetLoadedMachine(dim, event.to_x, event.to_y, event.to_z)
    if not isinstance(end_m, RFRepeaterPlant):
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_END, sub_status_code=0
        ).send(event.player_id)
        logger.warning(
            "[SkyblueTech] RFRepeaterPlant: player built invalid end plant at {}: {}".format(
                (event.to_x, event.to_y, event.to_z), end_m
            )
        )
        return
    elif not end_m.is_base_block:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INVALID_END, sub_status_code=1
        ).send(event.player_id)
        logger.warning(
            "[SkyblueTech] RFRepeaterPlant: player built invalid end plant layer at {}: {}".format(
                (event.to_x, event.to_y, event.to_z), end_m.layer
            )
        )
        return
    start_pos = (event.x, event.y, event.z)
    end_pos = (event.to_x, event.to_y, event.to_z)
    start_nearby_nodes = start_m.get_nearconn_plants()
    end_nearby_nodes = end_m.get_nearconn_plants()
    if start_nearby_nodes is None:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR, sub_status_code=0
        ).send(event.player_id)
        logger.error(
            "[SkyblueTech] RFRepeaterPlant: internal error at {}: start_nearby_nodes is None".format((
                event.to_x,
                event.to_y,
                event.to_z,
            ))
        )
        return
    elif end_nearby_nodes is None:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR, sub_status_code=1
        ).send(event.player_id)
        logger.error(
            "[SkyblueTech] RFRepeaterPlant: internal error at {}: end_nearby_nodes is None".format((
                event.to_x,
                event.to_y,
                event.to_z,
            ))
        )
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
    res, sub_stat_code = build_connection(dim, start_pos, end_pos)
    if not res:
        RFRepeaterPlantBuildResponse(
            RFRepeaterPlantBuildResponse.STATUS_INTERNAL_ERROR2,
            sub_status_code=sub_stat_code,
        ).send(event.player_id)
        logger.error(
            "[SkyblueTech] RFRepeaterPlant: internal error at {}: build_connection failed: {}".format(
                (
                    event.to_x,
                    event.to_y,
                    event.to_z,
                ),
                sub_stat_code,
            )
        )
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

    dim = CF.CreateDimension(event.player_id).GetEntityDimensionId()
    m = GetLoadedMachine(dim, event.x, event.y, event.z)
    if not isinstance(m, RFRepeaterPlant):
        return
    if not m.is_base_block:
        return
    if event.io_mode not in {MODE_INPUT, MODE_OUTPUT}:
        return
    change_node_mode(dim, event.x, event.y, event.z, event.io_mode)
