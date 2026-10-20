# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetPlayerDimensionId,
    SetOnePopupNotice,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from ...common.events.misc.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckMultiResponse,
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
)
from ..export.transmitter_visual_checker import (
    RegisterTransmitterType,
    _get_transmitter_types,
)
from ..transmitters.item_pipe.logic import logic_module as item_pipe_logic
from ..transmitters.fluid_pipe.logic import logic_module as fluid_pipe_logic
from ..transmitters.wire.logic import logic_module as wire_logic

RATE_LIMIT = 0.5

server_limiter = PlayerRateLimiter(RATE_LIMIT)

RegisterTransmitterType("skybluetech:item_pipe", "物品", item_pipe_logic)
RegisterTransmitterType("skybluetech:fluid_pipe", "流体", fluid_pipe_logic)
RegisterTransmitterType("skybluetech:wire", "能量", wire_logic, "用电器", "能量源")


def _make_response(registration, network):
    # type: (...) -> TransmitterVisualCheckerCheckResponse
    return TransmitterVisualCheckerCheckResponse(
        nodes=list(network.nodes),
        inputs=[ap.target_pos for ap in network.group_inputs],
        outputs=[ap.target_pos for ap in network.group_outputs],
        type_id=registration.type_id,
        display_name=registration.display_name,
        input_label=registration.input_label,
        output_label=registration.output_label,
    )


@TransmitterVisualCheckerCheckRequest.Listen()
def onRecvRequest(event):
    # type: (TransmitterVisualCheckerCheckRequest) -> None
    ok = server_limiter.record(event.player_id)
    if not ok:
        SetOnePopupNotice(event.player_id, "§c操作过快， 请稍后再试")
        return
    if event.mode not in (
        event.MODE_AUTO,
        event.MODE_GET_BY_TRANSMITTER,
        event.MODE_GET_BY_MACHINE,
    ):
        return
    dim = GetPlayerDimensionId(event.player_id)
    bname = GetBlockName(dim, (event.x, event.y, event.z))
    if bname is None:
        SetOnePopupNotice(event.player_id, "§6未找到网络")
        return
    registrations = _get_transmitter_types()
    if event.mode != event.MODE_GET_BY_MACHINE:
        for registration in registrations:
            logic = registration.logic_module
            if not logic.transmitter_check_func(bname):
                continue
            network = logic.GetNetworkByTransmitter(dim, event.x, event.y, event.z)
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
            else:
                _make_response(registration, network).send(event.player_id)
            return
        if event.mode == event.MODE_GET_BY_TRANSMITTER:
            SetOnePopupNotice(event.player_id, "§6未识别到传输网络")
            return
    responses = []
    for registration in registrations:
        logic = registration.logic_module
        if not logic.transmittable_block_check_func(
            bname, dim, (event.x, event.y, event.z)
        ):
            continue
        cnode = logic.GetContainerNode(dim, event.x, event.y, event.z)
        networks = set(cnode.get_inputs().values()) | set(cnode.get_outputs().values())
        for network in networks:
            responses.append(_make_response(registration, network))
    TransmitterVisualCheckerCheckMultiResponse(responses).send(event.player_id)
    if not responses:
        SetOnePopupNotice(event.player_id, "§6未找到网络")
