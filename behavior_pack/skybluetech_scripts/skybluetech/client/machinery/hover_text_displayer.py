# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent,
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

from ...common.define.id_enum import Machinery
from ...common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
)
from ...common.utils.block_sync import BlockSync

if 0 > 1:
    from typing import Any

block_sync = BlockSync(Machinery.HOVER_TEXT_DISPLAYER, side=BlockSync.SIDE_CLIENT)
shapes = {}  # type: dict[int, dict[tuple[int, int, int], Any]]


def add_text(dim, pos, default_text=""):
    # type: (int, tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    remove_text(dim, pos)
    shape = CF.CreateDrawing(LEVEL_ID).AddTextShape((tx, ty, tz), default_text)
    shapes.setdefault(dim, {})[pos] = shape


def remove_text(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    shape = shapes.get(dim, {}).pop(pos, None)
    if shape:
        shape.Remove()


def update_text(dim, pos, text):
    # type: (int, tuple[int, int, int], str) -> None
    shape = shapes.get(dim, {}).get(pos, None)
    if shape is not None:
        shape.SetText(text)


@asModBlockLoadedListener(Machinery.HOVER_TEXT_DISPLAYER)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    if pos not in shapes.get(event.dimensionId, {}):
        # 文本由服务端响应 BlockSync 的加载通知，避免读取尚未同步的 NBT。
        add_text(event.dimensionId, pos)


@asModBlockRemovedListener(Machinery.HOVER_TEXT_DISPLAYER)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    remove_text(event.dimensionId, pos)


@HoverTextDisplayerContentUpdate.Listen()
def onTextUpdated(event):
    # type: (HoverTextDisplayerContentUpdate) -> None
    if event.dimension_id != CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension():
        return
    update_text(
        event.dimension_id,
        (event.x, event.y, event.z),
        event.new_text,
    )


@DimensionChangeClientEvent.Listen()
def onChangeDimension(event):
    # type: (DimensionChangeClientEvent) -> None
    for pos in tuple(shapes.get(event.fromDimensionId, {})):
        remove_text(event.fromDimensionId, pos)
