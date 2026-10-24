# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from mod.client.extraClientApi import GetLocalPlayerId, GetMinecraftEnum
from skybluetech_scripts.tooldelta.utils.timer import Delay
from random import random
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ...common.events.misc.transmitter_visual_checker import (
    TransmitterVisualCheckerCheckRequest,
    TransmitterVisualCheckerCheckResponse,
    TransmitterVisualCheckerCheckMultiResponse,
)

RATE_LIMIT = 0.5


# CLIENT PART

client_limiter = PlayerRateLimiter(RATE_LIMIT)
g_shapes = []
g_multi_shapes = []


@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    mh_item_data = CF.CreateItem(GetLocalPlayerId()).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED, 0, True
    )
    mh_item = Item.from_dict(mh_item_data) if mh_item_data is not None else None
    if mh_item is None or mh_item.id != "skybluetech:transmitter_visual_checker":
        return
    ok = client_limiter.record(GetLocalPlayerId())
    if not ok:
        return
    TransmitterVisualCheckerCheckRequest(
        event.x,
        event.y,
        event.z,
        TransmitterVisualCheckerCheckRequest.MODE_AUTO,
    ).send()
    event.cancel()


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
    draw_comp = CF.CreateDrawing(LEVEL_ID)
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
        text_map.setdefault(input_node, []).append((event.input_label, (0, 1, 0)))
    for output_node in event.outputs:
        text_map.setdefault(output_node, []).append((event.output_label, (1, 0, 0)))
    for coord, labels in text_map.items():
        x, y, z = coord
        if len(labels) == 1:
            text, color = labels[0]
            text = (u"§a" if color == (0, 1, 0) else u"§c") + text
        else:
            text = u"\n".join((u"§a" if c == (0, 1, 0) else u"§c") + t for t, c in labels)
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
    draw_comp = CF.CreateDrawing(LEVEL_ID)
    _DXYZ_FACING = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    text_map = {}
    for response in event.reses:
        inputs, outputs, nodes = response.inputs, response.outputs, response.nodes
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
            label = response.display_name + u"： " + response.input_label
            text_map.setdefault(input_node, []).append((label, (0, 1, 0)))
        for output_node in outputs:
            label = response.display_name + u"： " + response.output_label
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
            text = (u"§a" if color == (0, 1, 0) else u"§c") + text
        else:
            text = u"\n".join((u"§a" if c == (0, 1, 0) else u"§c") + t for t, c in unique_labels)
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
