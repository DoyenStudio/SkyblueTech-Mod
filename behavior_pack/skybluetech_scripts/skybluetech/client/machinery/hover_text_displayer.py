# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.api.client import CreateShapeFactory
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode
from ...common.define.id_enum.machinery import HOVER_TEXT_DISPLAYER as MACHINE_ID
from ...common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
)
from ...common.machinery.utils.block_sync import BlockSync
from .utils.mod_block_event import asModBlockLoadedListener, asModBlockRemovedListener

if 0:
    from typing import Any

block_sync = BlockSync(MACHINE_ID)
shapes = {}  # type: dict[tuple[int, int, int], Any]


def add_text(pos, default_text=""):
    # type: (tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    shape = CreateShapeFactory().AddTextShape((tx, ty, tz), default_text)
    shapes[pos] = shape


def remove_text(pos):
    # type: (tuple[int, int, int]) -> None
    shape = shapes.pop(pos, None)
    if shape:
        shape.Remove()


def update_text(pos, text):
    # type: (tuple[int, int, int], str) -> None
    shape = shapes.get(pos, None)
    if shape is not None:
        shape.SetText(text)


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    if pos not in shapes:
        add_text(pos)


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    remove_text(pos)


@HoverTextDisplayerContentUpdate.Listen()
def onTextUpdated(event):
    # type: (HoverTextDisplayerContentUpdate) -> None
    update_text((event.x, event.y, event.z), event.new_text)
