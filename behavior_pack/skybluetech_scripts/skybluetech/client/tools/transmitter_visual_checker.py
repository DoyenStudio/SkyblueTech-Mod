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
from skybluetech_scripts.skybluetech.common.define.id_enum import ItemPipe, FluidPipe, Wire
from ...common.events.misc.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
    TransmitterVisualCheckerCheckMultiResponse,
)

CF = GetEngineCompFactory()
RATE_LIMIT = 0.5
TRANSMITTER_BLOCK_IDS = ItemPipe.all() | FluidPipe.all() | Wire.all()


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
    if bname in TRANSMITTER_BLOCK_IDS:
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
    text_map = {} # type: dict[tuple[int, int, int], list[tuple[str, tuple]]]
    for input_node in event.inputs:
        label = "用电器" if event.type == event.TYPE_WIRE else "输入"
        text_map.setdefault(input_node, []).append((label, (0, 1, 0)))
    for output_node in event.outputs:
        label = "能量源" if event.type == event.TYPE_WIRE else "抽取"
        text_map.setdefault(output_node, []).append((label, (1, 0, 0)))
    for coord, labels in text_map.items():
        x, y, z = coord
        if len(labels) == 1:
            text, color = labels[0]
            text = ("§a" if color == (0, 1, 0) else "§c") + text
        else:
            text = "\n".join(("§a" if c == (0, 1, 0) else "§c") + t for t, c in labels)
        shape = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            text,
            (1, 1, 1),
        )
        shapes.append(shape)
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
    text_map = {}
    for inputs, outputs, nodes, network_type in event.reses:
        box_color = (random(), random(), random())
        all_nodes = set(nodes) | set(inputs + outputs)
        for nx, ny, nz in all_nodes:
            for dx, dy, dz in _DXYZ_FACING:
                if (nx + dx, ny + dy, nz + dz) in all_nodes:
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
            label = NETWORK_TYPE_ZHCN[network_type] + "： 输入"
            text_map.setdefault(input_node, []).append((label, (0, 1, 0)))
        for output_node in outputs:
            label = NETWORK_TYPE_ZHCN[network_type] + "： 抽取"
            text_map.setdefault(output_node, []).append((label, (1, 0, 0)))
    for coord, labels in text_map.items():
        x, y, z = coord
        # 去重：使用集合去除重复的标签
        unique_labels = []
        seen = set()
        for label, color in labels:
            key = (label, color)
            if key not in seen:
                seen.add(key)
                unique_labels.append((label, color))
        if len(unique_labels) == 1:
            text, color = unique_labels[0]
            text = ("§a" if color == (0, 1, 0) else "§c") + text
        else:
            text = "\n".join(("§a" if c == (0, 1, 0) else "§c") + t for t, c in unique_labels)
            color = (1, 1, 1)
        shape = draw_comp.AddTextShape(
            (x + 0.5, y + 0.5, z + 0.5),
            text,
            color,
        )
        shapes.append(shape)
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
