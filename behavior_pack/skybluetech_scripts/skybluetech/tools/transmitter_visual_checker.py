# coding=utf-8
from random import random
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId, GetBlockName, SetOnePopupNotice
from skybluetech_scripts.tooldelta.api.client import GetLocalPlayerMainhandItem, GetLocalPlayerId, GetBlockName as CGetBlockName
from skybluetech_scripts.tooldelta.api.timer import Delay
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.internal import ClientComp, ClientLevelId
from skybluetech_scripts.tooldelta.extensions.player_rate_limit import PlayerRateLimiter
from ..define.events.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
    TransmitterVisualCheckerCheckMultiResponse,
)
from ..transmitters.constants import DXYZ_FACING
from ..transmitters.cable.logic import GetNetworkByCable, GetNearbyCableNetworks, isCable
from ..transmitters.pipe.logic import GetNetworkByPipe, GetNearbyPipeNetworks, isPipe
from ..transmitters.wire.logic import GetNetworkByWire, GetNearbyWireNetworks, isWire

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
            network = GetNetworkByCable(dim, event.x, event.y, event.z)
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
                return
            network_type = TransmitterVisualCheckerCheckResponse.TYPE_CABLE
        elif isPipe(bname):
            network = GetNetworkByPipe(dim, event.x, event.y, event.z)
            if network is None:
                SetOnePopupNotice(event.player_id, "§6未找到网络")
                return
            network_type = TransmitterVisualCheckerCheckResponse.TYPE_PIPE
        elif isWire(bname):
            network = GetNetworkByWire(dim, event.x, event.y, event.z)
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
        T(
            [
                (
                    [ap.target_pos for ap in network.group_inputs],
                    [ap.target_pos for ap in network.group_outputs],
                    [node for node in network.nodes],
                    network_type,
                )
                for (i, o), network_type in (
                    (GetNearbyCableNetworks(dim, event.x, event.y, event.z), T.TYPE_CABLE),
                    (GetNearbyPipeNetworks(dim, event.x, event.y, event.z), T.TYPE_PIPE),
                    (GetNearbyWireNetworks(dim, event.x, event.y, event.z), T.TYPE_WIRE),
                )
                for network in i + o
            ]
        ).send(event.player_id)
            
        


# CLIENT PART

client_limiter = PlayerRateLimiter(RATE_LIMIT)
g_shapes = []
g_multi_shapes = []
NETWORK_TYPE_ZHCN = (
    "物品",
    "流体",
    "能量",
)

@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    mh_item = GetLocalPlayerMainhandItem()
    if mh_item is None or mh_item.id != "skybluetech:transmitter_visual_checker":
        return
    ok = client_limiter.record(GetLocalPlayerId())
    if not ok:
        return
    bname = CGetBlockName((event.x, event.y, event.z))
    if bname is None:
        return
    if "cable" in bname or "pipe" in bname or "wire" in bname:
        TransmitterVisualCheckerCheckRequest(
            event.x, event.y, event.z,
            TransmitterVisualCheckerCheckRequest.MODE_GET_BY_TRANSMITTER,
        ).send()
    else:
        TransmitterVisualCheckerCheckRequest(
            event.x, event.y, event.z,
            TransmitterVisualCheckerCheckRequest.MODE_GET_BY_MACHINE,
        ).send()
    event.cancel()

# @PlayerTryDestroyBlockClientEvent.Listen()
# def onClientBlockDestroyEvent(event):
#     # type: (PlayerTryDestroyBlockClientEvent) -> None
#     mh_item = GetLocalPlayerMainhandItem()
#     if mh_item is None or mh_item.id != "skybluetech:transmitter_visual_checker":
#         return
#     TransmitterVisualCheckerCheckRequest(
#         event.x, event.y, event.z,
#         TransmitterVisualCheckerCheckRequest.MODE_GET_BY_MACHINE,
#     ).send()
#     event.cancel()
#     print("Canceled")


@TransmitterVisualCheckerCheckResponse.Listen()
def onResponse(event):
    # type: (TransmitterVisualCheckerCheckResponse) -> None
    displayModel(event)

@TransmitterVisualCheckerCheckMultiResponse.Listen()
def onMultiResponse(event):
    # type: (TransmitterVisualCheckerCheckMultiResponse) -> None
    displayMultiModel(event)

def displayModel(event):
    # type: (TransmitterVisualCheckerCheckResponse) -> None
    clean()
    shapes = []
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
                shapes.append(box)
    for input_node in event.inputs:
        x, y, z = input_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "用电器" if event.type == event.TYPE_WIRE else "输入",
            (0, 1, 0)
        )
        shapes.append(text)
    for output_node in event.outputs:
        x, y, z = output_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "能量源" if event.type == event.TYPE_WIRE else "抽取",
            (1, 0, 0)
        )
        shapes.append(text)
    g_shapes.append(shapes)
    removeAfter(shapes)

@Delay(10)
def removeAfter(shapes):
    if shapes in g_shapes:
        g_shapes.remove(shapes)
        for shape in shapes:
            shape.Remove()

def clean():
    for shape in [j for i in g_shapes for j in i]:
        shape.Remove()
    g_shapes[:] = []
    for shape in [j for i in g_multi_shapes for j in i]:
        shape.Remove()
    g_multi_shapes[:] = []



def displayMultiModel(event):
    # type: (TransmitterVisualCheckerCheckMultiResponse) -> None
    clean()
    shapes = []
    draw_comp = ClientComp.CreateDrawing(ClientLevelId)
    for (inputs, outputs, nodes, network_type) in event.reses:
        box_color = (random(), random(), random())
        nodes = set(nodes)
        all_nodes = nodes | set(inputs + outputs)
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
                        box_color
                    )
                    shapes.append(box)
        for input_node in inputs:
            x, y, z = input_node
            text = draw_comp.AddTextShape(
                (x + 0.5, y + 0.3 + 0.2 * network_type, z + 0.5),
                NETWORK_TYPE_ZHCN[network_type] + "： 输入",
                (0, 1, 0)
            )
            shapes.append(text)
        for output_node in outputs:
            x, y, z = output_node
            text = draw_comp.AddTextShape(
                (x + 0.5, y + 0.3 + 0.2 * network_type, z + 0.5),
                NETWORK_TYPE_ZHCN[network_type] + "： 抽取",
                (1, 0, 0)
            )
            shapes.append(text)
    g_multi_shapes.append(shapes)
    removeMultiAfter(shapes)

@Delay(10)
def removeMultiAfter(shapes):
    if shapes in g_multi_shapes:
        g_multi_shapes.remove(shapes)
        for shape in shapes:
            shape.Remove()

