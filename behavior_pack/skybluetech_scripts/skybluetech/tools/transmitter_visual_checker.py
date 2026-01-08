# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId, GetBlockName, SetOnePopupNotice
from skybluetech_scripts.tooldelta.api.client import SePopupNotice, GetLocalPlayerMainhandItem, GetLocalPlayerId
from skybluetech_scripts.tooldelta.api.timer import Delay
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.internal import ClientComp, ClientLevelId
from skybluetech_scripts.tooldelta.extensions.player_rate_limit import PlayerRateLimiter
from ..define.events.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
)
from ..transmitters.constants import DXYZ_FACING
from ..transmitters.cable.logic import GetNetworkByCable, isCable
from ..transmitters.pipe.logic import GetNetworkByPipe, isPipe
from ..transmitters.wire.logic import GetNetworkByWire, isWire

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
        TransmitterVisualCheckerCheckResponse(suc=False).send(event.player_id)
        return
    if isCable(bname):
        network = GetNetworkByCable(dim, event.x, event.y, event.z)
        if network is None:
            TransmitterVisualCheckerCheckResponse(suc=False).send(event.player_id)
            return
        network_type = TransmitterVisualCheckerCheckResponse.TYPE_CABLE
    elif isPipe(bname):
        network = GetNetworkByPipe(dim, event.x, event.y, event.z)
        if network is None:
            TransmitterVisualCheckerCheckResponse(suc=False).send(event.player_id)
            return
        network_type = TransmitterVisualCheckerCheckResponse.TYPE_PIPE
    elif isWire(bname):
        network = GetNetworkByWire(dim, event.x, event.y, event.z)
        if network is None:
            TransmitterVisualCheckerCheckResponse(suc=False).send(event.player_id)
            return
        network_type = TransmitterVisualCheckerCheckResponse.TYPE_WIRE
    else:
        TransmitterVisualCheckerCheckResponse(suc=False).send(event.player_id)
        return
    TransmitterVisualCheckerCheckResponse(
        suc=True,
        nodes=list(network.nodes),
        inputs=[i.target_pos for i in network.group_inputs],
        outputs=[i.target_pos for i in network.group_outputs],
        type=network_type,
    ).send(event.player_id)


# CLIENT PART

client_limiter = PlayerRateLimiter(RATE_LIMIT)
g_shapes = []

@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    mh_item = GetLocalPlayerMainhandItem()
    if mh_item is None or mh_item.id != "skybluetech:transmitter_visual_checker":
        return
    if event.blockName.startswith("skybluetech:") and (
        "cable" in event.blockName
        or "pipe" in event.blockName 
        or "wire" in event.blockName
    ):
        ok = client_limiter.record(GetLocalPlayerId())
        if not ok:
            return
        TransmitterVisualCheckerCheckRequest(
            event.x, event.y, event.z
        ).send()

@TransmitterVisualCheckerCheckResponse.Listen()
def onResponse(event):
    # type: (TransmitterVisualCheckerCheckResponse) -> None
    if not event.suc:
        SePopupNotice("§6未找到网络")
    else:
        displayModel(event)

def displayModel(event):
    # type: (TransmitterVisualCheckerCheckResponse) -> None
    clean()
    draw_comp = ClientComp.CreateDrawing(ClientLevelId)
    nodes = set(event.nodes)
    all_nodes = nodes | set(event.inputs + event.outputs)
    for nx, ny, nz in nodes:
        for dx, dy, dz in DXYZ_FACING:
            if (nx + dx, ny + dy, nz + dz) in all_nodes:
                # line = draw_comp.AddLineShape(
                #     (nx + 0.5, ny + 1, nz + 0.5),
                #     (nx + dx + 0.5, ny + dy + 1, nz + dz + 0.5),
                #     (0, 1, 1)
                # )
                min_x = min(nx, nx + dx)
                min_y = min(ny, ny + dy)
                min_z = min(nz, nz + dz)
                ddx = 1.2 if dx != 0 else 0.2
                ddy = 1.2 if dy != 0 else 0.2
                ddz = 1.2 if dz != 0 else 0.2
                box = draw_comp.AddBoxShape(
                    (min_x + 0.4, min_y + 1, min_z + 0.4),
                    (ddx, ddy, ddz),
                    (0, 1, 1)
                )
                g_shapes.append(box)
    for input_node in event.inputs:
        x, y, z = input_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "用电器" if event.type == event.TYPE_WIRE else "输入",
            (0, 1, 0)
        )
        g_shapes.append(text)
    for output_node in event.outputs:
        x, y, z = output_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "能量源" if event.type == event.TYPE_WIRE else "输出",
            (1, 0, 0)
        )
        g_shapes.append(text)
    removeAfter()

@Delay(10)
def removeAfter():
    clean()

def clean():
    for shape in g_shapes:
        shape.Remove()