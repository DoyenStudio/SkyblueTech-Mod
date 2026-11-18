# coding=utf-8
from time import time

from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent, ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from skybluetech_scripts.tooldelta.utils.timer import Repeat

from ...common.define.id_enum import Machinery
from ...common.machinery_def.basic import FluidSlotClient
from ...common.machinery_def.industrial_centrifuge import K_WORKING
from ..utils.fluid_texture_frames import FLUID_TEXTURE_TINTS

_loaded = {}


def _tube_appearance(info, fluid_id):
    face = ((info.GetBlockTextures(fluid_id) or {}).get("Up") or {}) if fluid_id else {}
    texture_key = face.get("name")
    region = info.GetTextureAtlasUV(texture_key) if texture_key else None
    if not region or region[2] <= 0 or region[3] <= 0:
        return (0, 0, 0, 1, 1, 1, 1, 1)
    # 原版水的地形图块为灰度，复用储罐的染色参数。
    paths = face.get("paths")
    tint = FLUID_TEXTURE_TINTS.get(paths[0]) if paths else None
    return (1,) + tuple(region) + (tint[:3] if tint else (1, 1, 1))


def _refresh(info, key):
    dim, x, y, z = key
    data = info.GetBlockEntityData((x, y - 1, z))
    if not data or "exData" not in data:
        return
    data = data["exData"]
    slots = [FluidSlotClient(data, i) for i in range(3)]
    fluids = tuple(slot.fluid_id if slot.volume > 0 else None for slot in slots)
    working = int(bool(GetValueWithDefault(data, K_WORKING, False)))
    block = info.GetBlock((x, y, z))
    if not block or block[0] != Machinery.INDUSTRIAL_CENTRIFUGE_UPSIDE:
        return
    state = (working, fluids, block[1])
    last_state, retry_at = _loaded[key]
    if last_state == state and (not retry_at or time() < retry_at):
        return
    # Cardinal aux order: south, west, north, east.
    yaw = (180, 90, 0, -90)[block[1] & 3]
    values = [("working", working), ("yaw", yaw)]
    retry_at = 0
    for n, fluid_id in enumerate(fluids, 1):
        tube = "tube%d" % n
        appearance = _tube_appearance(info, fluid_id)
        if fluid_id and not appearance[0]:
            # 进世界时方块数据可能早于地形图集就绪。
            retry_at = time() + 2
        values.extend((tube + suffix, value) for suffix, value in zip(
            ("", "_u", "_v", "_w", "_h", "_r", "_g", "_b"), appearance
        ))
    if all(info.SetBlockEntityMolangValue((x, y, z), "variable." + name, float(value))
           for name, value in values):
        _loaded[key] = (state, retry_at)


@ModBlockEntityLoadedClientEvent.Listen()
def _on_load(event):
    if event.blockName == Machinery.INDUSTRIAL_CENTRIFUGE_UPSIDE:
        key = (event.dimensionId, event.posX, event.posY, event.posZ)
        _loaded[key] = (None, 0)
        _refresh(CF.CreateBlockInfo(LEVEL_ID), key)


@ModBlockEntityRemoveClientEvent.Listen()
def _on_remove(event):
    if event.blockName == Machinery.INDUSTRIAL_CENTRIFUGE_UPSIDE:
        _loaded.pop((event.dimensionId, event.posX, event.posY, event.posZ), None)


@ClientInitCallback()
@Repeat(0.1)
def _update():
    if _loaded:
        info = CF.CreateBlockInfo(LEVEL_ID)
        dim = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
        for key in tuple(_loaded):
            if key[0] == dim:
                _refresh(info, key)


@DimensionChangeClientEvent.Listen()
def _change_dimension(event):
    for key in tuple(_loaded):
        if key[0] == event.fromDimensionId:
            _loaded.pop(key, None)


@ClientUninitCallback()
def _uninit():
    _loaded.clear()
