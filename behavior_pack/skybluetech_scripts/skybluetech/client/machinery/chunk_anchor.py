# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent,
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from skybluetech_scripts.tooldelta.utils.timer import Repeat

from ...common.machinery_def.chunk_anchor import ANCHOR, BEAM, BEAM_OFF


loaded_anchors = {}


def _refresh(block_info, key):
    pos = key[1:]
    data = (block_info.GetBlockEntityData(pos) or {}).get("exData", {})
    beam = GetValueWithDefault(data, BEAM, BEAM_OFF)
    if loaded_anchors[key] != beam:
        if block_info.SetBlockEntityMolangValue(pos, "variable.anchor_beam", float(beam)):
            loaded_anchors[key] = beam


@ModBlockEntityLoadedClientEvent.Listen()
def _on_load(event):
    if event.blockName == ANCHOR:
        key = (event.dimensionId, event.posX, event.posY, event.posZ)
        loaded_anchors[key] = None
        _refresh(CF.CreateBlockInfo(LEVEL_ID), key)


@ModBlockEntityRemoveClientEvent.Listen()
def _on_remove(event):
    if event.blockName == ANCHOR:
        loaded_anchors.pop((event.dimensionId, event.posX, event.posY, event.posZ), None)


@ClientInitCallback()
@Repeat(0.1)
def _update():
    if loaded_anchors:
        block_info = CF.CreateBlockInfo(LEVEL_ID)
        dim = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
        for key in tuple(loaded_anchors):
            if key[0] == dim:
                _refresh(block_info, key)


@DimensionChangeClientEvent.Listen()
def _on_dimension_changed(event):
    for key in tuple(loaded_anchors):
        if key[0] == event.fromDimensionId:
            loaded_anchors.pop(key, None)


@ClientUninitCallback()
def _on_client_uninit():
    loaded_anchors.clear()
