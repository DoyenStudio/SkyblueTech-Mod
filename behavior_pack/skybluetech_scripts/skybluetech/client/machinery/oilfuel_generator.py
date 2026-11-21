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

from ...common.define.id_enum import Machinery
from ...common.machinery_def.basic import K_DEACTIVE_FLAGS
from ...common.machinery_def.oilfuel_generator import K_MODEL_YAW


loaded_generators = {}


def _refresh(block_info, key):
    pos = key[1:]
    data = (block_info.GetBlockEntityData(pos) or {}).get("exData", {})
    yaw = GetValueWithDefault(data, K_MODEL_YAW, None)
    if yaw is None:
        return
    working = int(GetValueWithDefault(data, K_DEACTIVE_FLAGS, None) == 0)
    state = (yaw, working)
    if loaded_generators.get(key) == state:
        return
    ok_yaw = block_info.SetBlockEntityMolangValue(pos, "variable.yaw", yaw)
    ok_working = block_info.SetBlockEntityMolangValue(pos, "variable.working", working)
    if ok_yaw and ok_working:
        loaded_generators[key] = state


@ModBlockEntityLoadedClientEvent.Listen()
def _on_load(event):
    if event.blockName == Machinery.OILFUEL_GENERATOR:
        key = (event.dimensionId, event.posX, event.posY, event.posZ)
        loaded_generators[key] = None
        _refresh(CF.CreateBlockInfo(LEVEL_ID), key)


@ModBlockEntityRemoveClientEvent.Listen()
def _on_remove(event):
    if event.blockName == Machinery.OILFUEL_GENERATOR:
        loaded_generators.pop((event.dimensionId, event.posX, event.posY, event.posZ), None)


@ClientInitCallback()
@Repeat(0.1)
def _update():
    if loaded_generators:
        block_info = CF.CreateBlockInfo(LEVEL_ID)
        dim = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
        for key in tuple(loaded_generators):
            if key[0] == dim:
                _refresh(block_info, key)


@DimensionChangeClientEvent.Listen()
def _on_dimension_changed(event):
    for key in tuple(loaded_generators):
        if key[0] == event.fromDimensionId:
            loaded_generators.pop(key, None)


@ClientUninitCallback()
def _on_client_uninit():
    loaded_generators.clear()
