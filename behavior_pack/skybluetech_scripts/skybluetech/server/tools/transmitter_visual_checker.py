# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import (
    GetPlayerDimensionId,
    GetBlockName,
    SetOnePopupNotice,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ...common.events.misc.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
    TransmitterVisualCheckerCheckMultiResponse,
)
from ..transmitters.cable.logic import logic_module as cable_logic, isCable
from ..transmitters.pipe.logic import logic_module as pipe_logic, isPipe
from ..transmitters.wire.logic import logic_module as wire_logic, isWire

RATE_LIMIT = 0.5

server_limiter = PlayerRateLimiter(RATE_LIMIT)

# SERVER PART


@TransmitterVisualCheckerCheckRequest.Listen()
def onRecvRequest(event):
    # type: (TransmitterVisualCheckerCheckRequest) -> None
    ok = server_limiter.record(event.player_id)
    if not ok:
        SetOnePopupNotice(event.player_id, "§c操作过快， 请稍后再试")
        return
    dim = GetPlayerDimensionId(event.player_id)
    bname = GetBlockName(dim, (event.x, event.y, event.z))
    if bname is None:
        SetOnePopupNotice(event.player_id, "§6未找到网络")
        return
    if event.mode == event.MODE_GET_BY_TRANSMITTER:
        if isCable(bname):
            network = cable_logic.GetNetworkByTransmitter(
                dim, event.x, event.y, event.z
            )
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
                return
            network_type = TransmitterVisualCheckerCheckResponse.TYPE_CABLE
        elif isPipe(bname):
            network = pipe_logic.GetNetworkByTransmitter(dim, event.x, event.y, event.z)
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
                return
            network_type = TransmitterVisualCheckerCheckResponse.TYPE_PIPE
        elif isWire(bname):
            network = wire_logic.GetNetworkByTransmitter(dim, event.x, event.y, event.z)
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
                return
            network_type = TransmitterVisualCheckerCheckResponse.TYPE_WIRE
        else:
            SetOnePopupNotice(event.player_id, "§6未识别到传输网络")
            return
        TransmitterVisualCheckerCheckResponse(
            nodes=list(network.nodes),
            inputs=[i.target_pos for i in network.group_inputs],
            outputs=[i.target_pos for i in network.group_outputs],
            type=network_type,
        ).send(event.player_id)
    else:
        T = TransmitterVisualCheckerCheckMultiResponse
        T([
            (
                [ap.target_pos for ap in network.group_inputs],
                [ap.target_pos for ap in network.group_outputs],
                [node for node in network.nodes],
                network_type,
            )
            for cnode, network_type in (
                (
                    cable_logic.GetContainerNode(dim, event.x, event.y, event.z),
                    T.TYPE_CABLE,
                ),
                (
                    pipe_logic.GetContainerNode(dim, event.x, event.y, event.z),
                    T.TYPE_PIPE,
                ),
                (
                    wire_logic.GetContainerNode(dim, event.x, event.y, event.z),
                    T.TYPE_WIRE,
                ),
            )
            for network in set(i for i in cnode.inputs.values() if i is not None)
            | set(o for o in cnode.outputs.values() if o is not None)
        ]).send(event.player_id)
