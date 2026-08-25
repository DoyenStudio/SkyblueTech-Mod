# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import (
    CreateShapeFactory,
    GetBlockEntityData,
    GetPlayerDimensionId,
)
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent,
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.utils import nbt

from ...common.define.id_enum.machinery import Machinery
from ...common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
)
from ...common.machinery_def.basic.base_machine import K_DEACTIVE_FLAGS
from ...common.machinery_def.hover_text_displayer import K_TEXT
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
    if pos in shapes:
        shapes.pop(pos).Remove()
    shape = CreateShapeFactory().AddTextShape((tx, ty, tz), default_text)
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


def init_text(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    add_text(dim, pos)
    block_nbt = GetBlockEntityData(*pos)
    if block_nbt is None:
        return
    text = nbt.GetValueWithDefault(block_nbt["exData"], K_TEXT, None)
    deactive_flags = nbt.GetValueWithDefault(block_nbt["exData"], K_DEACTIVE_FLAGS, 0)
    if deactive_flags == 0 and text is not None:
        update_text(dim, pos, text)


@asModBlockLoadedListener(Machinery.HOVER_TEXT_DISPLAYER)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    if pos not in shapes:
        init_text(GetPlayerDimensionId(), pos)


@asModBlockRemovedListener(Machinery.HOVER_TEXT_DISPLAYER)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    remove_text(GetPlayerDimensionId(), pos)


@HoverTextDisplayerContentUpdate.Listen()
def onTextUpdated(event):
    # type: (HoverTextDisplayerContentUpdate) -> None
    update_text(GetPlayerDimensionId(), (event.x, event.y, event.z), event.new_text)


@DimensionChangeClientEvent.Listen()
def onChangeDimension(event):
    # type: (DimensionChangeClientEvent) -> None
    for pos in tuple(shapes[event.fromDimensionId]):
        remove_text(event.fromDimensionId, pos)
