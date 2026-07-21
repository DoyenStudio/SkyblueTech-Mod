# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.api.client import (
    CreateShapeFactory,
    GetBlockEntityData,
)
from skybluetech_scripts.tooldelta.utils import nbt
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.HOVER_TEXT_DISPLAYER
from ...common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
)
from ...common.machinery_def.basic.base_machine import K_DEACTIVE_FLAGS
from ...common.machinery_def.hover_text_displayer import K_TEXT
from ...common.utils.block_sync import BlockSync
from ..utils.mod_block_event import asModBlockLoadedListener, asModBlockRemovedListener

if 0:
    from typing import Any

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_CLIENT)
shapes = {}  # type: dict[tuple[int, int, int], Any]


def add_text(pos, default_text=""):
    # type: (tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    if pos in shapes:
        shapes.pop(pos).Remove()
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


def init_text(pos):
    # type: (tuple[int, int, int]) -> None
    add_text(pos)
    block_nbt = GetBlockEntityData(*pos)
    if block_nbt is None:
        return
    text = nbt.GetValueWithDefault(block_nbt["exData"], K_TEXT, None)
    deactive_flags = nbt.GetValueWithDefault(block_nbt["exData"], K_DEACTIVE_FLAGS, 0)
    if deactive_flags == 0 and text is not None:
        update_text(pos, text)


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    if pos not in shapes:
        init_text(pos)


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    remove_text(pos)


@HoverTextDisplayerContentUpdate.Listen()
def onTextUpdated(event):
    # type: (HoverTextDisplayerContentUpdate) -> None
    update_text((event.x, event.y, event.z), event.new_text)
