# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId

from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.api.common import Repeat
from skybluetech_scripts.tooldelta.events.client.block import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault

from ...common.define.id_enum.machinery import Machinery
from ...common.machinery_def.creative_power_acceptor import K_POWER

if 0>1:
    from typing import Any

CF = GetEngineCompFactory()


texts = {}  # type: dict[tuple[int, tuple[int, int, int]], Any]


def add_text(dim, pos, default_text=""):
    # type: (int, tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    if (dim, pos) in texts:
        texts.pop((dim, pos)).Remove()
    t = CF.CreateDrawing(GetLevelId()).AddTextShape((tx, ty, tz), default_text)
    texts[(dim, pos)] = t


def remove_text(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    texts.pop((dim, pos)).Remove()


def update_text(text_shape, text):
    # type: (Any, str) -> None
    text_shape.SetText(text)


def get_power(x, y, z):
    b = GetBlockEntityData(x, y, z)
    if b is None:
        return None
    return GetValueWithDefault(b["exData"], K_POWER, -1)


@asModBlockLoadedListener(Machinery.CREATIVE_POWER_ACCEPTOR)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    add_text(event.dimensionId, (event.posX, event.posY, event.posZ), "输入功率： --")


@asModBlockRemovedListener(Machinery.CREATIVE_POWER_ACCEPTOR)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    remove_text(event.dimensionId, (event.posX, event.posY, event.posZ))


@ClientInitCallback()
@Repeat(1)
def onRepeat1s():
    for (dim, pos), text_shape in texts.copy().items():
        power = get_power(*pos)
        if power is None:
            del texts[(dim, pos)]
            continue
        else:
            update_text(text_shape, "输入功率： §a%d RF/t" % power)
