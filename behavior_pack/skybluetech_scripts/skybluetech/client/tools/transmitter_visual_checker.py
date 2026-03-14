# coding=utf-8
from random import random
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from skybluetech_scripts.tooldelta.api.client import (
    GetLocalPlayerMainhandItem,
    GetLocalPlayerId,
    GetBlockName as CGetBlockName,
)
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ...common.events.misc.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
    TransmitterVisualCheckerCheckMultiResponse,
)

CF = GetEngineCompFactory()
RATE_LIMIT = 0.5


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
            event.x,
            event.y,
            event.z,
            TransmitterVisualCheckerCheckRequest.MODE_GET_BY_TRANSMITTER,
        ).send()
    else:
        TransmitterVisualCheckerCheckRequest(
            event.x,
            event.y,
            event.z,
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
    draw_comp = CF.CreateDrawing(GetLevelId())
    nodes = set(event.nodes)
    all_nodes = nodes | set(event.inputs + event.outputs)
    for nx, ny, nz in nodes:
        for dx, dy, dz in (
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ):
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
                    (min_x + 0.4, min_y + 1, min_z + 0.4), (ddx, ddy, ddz), (0, 1, 1)
                )
                shapes.append(box)
    for input_node in event.inputs:
        x, y, z = input_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "用电器" if event.type == event.TYPE_WIRE else "输入",
            (0, 1, 0),
        )
        shapes.append(text)
    for output_node in event.outputs:
        x, y, z = output_node
        text = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            "能量源" if event.type == event.TYPE_WIRE else "抽取",
            (1, 0, 0),
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
    draw_comp = CF.CreateDrawing(GetLevelId())
    _DXYZ_FACING = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    for inputs, outputs, nodes, network_type in event.reses:
        box_color = (random(), random(), random())
        all_nodes = set(nodes) | set(inputs + outputs)
        for nx, ny, nz in all_nodes:
            for dx, dy, dz in _DXYZ_FACING:
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
                        box_color,
                    )
                    shapes.append(box)
        for input_node in inputs:
            x, y, z = input_node
            text = draw_comp.AddTextShape(
                (x + 0.5, y + 0.3 + 0.2 * network_type, z + 0.5),
                NETWORK_TYPE_ZHCN[network_type] + "： 输入",
                (0, 1, 0),
            )
            shapes.append(text)
        for output_node in outputs:
            x, y, z = output_node
            text = draw_comp.AddTextShape(
                (x + 0.5, y + 0.3 + 0.2 * network_type, z + 0.5),
                NETWORK_TYPE_ZHCN[network_type] + "： 抽取",
                (1, 0, 0),
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


@ClientInitCallback()
def onClientInit():
    ClientBlockUseEvent.AddExtraBlocks({"minecraft:chest", "minecraft:barrel"})
