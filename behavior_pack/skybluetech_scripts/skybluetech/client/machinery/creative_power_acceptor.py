# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.events.client.block import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from ...common.events.machinery.creative_power_acceptor import (
    CreativePowerAcceptorPowerUpdate,
    CreativePowerAcceptorPowerUpdateRequest,
)
from ...common.define.id_enum.machinery import CREATIVE_POWER_ACCEPTOR as MACHINE_ID
from .utils.mod_block_event import asModBlockRemovedListener, asModBlockLoadedListener

if 0:
    from typing import Any

CF = GetEngineCompFactory()
INFINITY = float("inf")


texts = {}  # type: dict[tuple[int, tuple[float, float, float]], Any]


def addText(dim, pos, default_text=""):
    # type: (int, tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    t = CF.CreateDrawing(GetLevelId()).AddTextShape((tx, ty, tz), default_text)
    texts[(dim, pos)] = t


def removeText(dim, pos):
    # type: (int, tuple[int, int, int]) -> None
    texts.pop((dim, pos)).Remove()


def updateText(dim, pos, text):
    # type: (int, tuple[int, int, int], str) -> None
    text_elem = texts.get((dim, pos), None)
    if text_elem is not None:
        text_elem.SetText(text)


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    addText(event.dimensionId, (event.posX, event.posY, event.posZ), "输入功率： --")
    CreativePowerAcceptorPowerUpdateRequest(
        event.dimensionId, event.posX, event.posY, event.posZ
    ).send()


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    removeText(event.dimensionId, (event.posX, event.posY, event.posZ))


@CreativePowerAcceptorPowerUpdate.Listen()
def onPowerUpdate(event):
    # type: (CreativePowerAcceptorPowerUpdate) -> None
    for dim, x, y, z, power in event.datas:
        if power == -1:
            text = "输入功率： §a无限 RF/t"
        else:
            text = "输入功率： §a%d RF/t" % power
        updateText(dim, (x, y, z), text)


@ClientInitCallback()
def onClientInit():
    CreativePowerAcceptorPowerUpdateRequest(-1, 0, 0, 0).send()
