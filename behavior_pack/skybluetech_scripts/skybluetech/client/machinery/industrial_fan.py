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
from ...common.machinery_def.industrial_fan import K_ANIM_SPEED


ROTATIONS = {
    0: (90, 0),
    1: (-90, 0),
    2: (0, 0),
    3: (0, 180),
    4: (0, -90),
    5: (0, 90),
}
loaded_fans = {}  # type: dict[tuple[int, int, int, int], tuple[int, int] | None]


def update_fan(key, block_info):
    xyz = key[1:]
    block_name, aux = block_info.GetBlock(xyz) or (None, 0)
    if block_name != Machinery.INDUSTRIAL_FAN:
        loaded_fans.pop(key, None)
        return
    block_data = block_info.GetBlockEntityData(xyz)
    speed = GetValueWithDefault(block_data.get("exData", {}), K_ANIM_SPEED, 0) if block_data else 0
    state = (aux & 7, speed)
    if loaded_fans.get(key) == state:
        return
    rot_x, rot_y = ROTATIONS[state[0]]
    ok_x = block_info.SetBlockEntityMolangValue(xyz, "variable.rotation_x", rot_x)
    ok_y = block_info.SetBlockEntityMolangValue(xyz, "variable.rotation_y", rot_y)
    ok_speed = block_info.SetBlockEntityMolangValue(xyz, "variable.skybluetech_fan_speed", speed)
    if ok_x and ok_y and ok_speed:
        loaded_fans[key] = state


@ModBlockEntityLoadedClientEvent.Listen()
def on_fan_loaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName != Machinery.INDUSTRIAL_FAN:
        return
    key = (event.dimensionId, event.posX, event.posY, event.posZ)
    loaded_fans[key] = None
    update_fan(key, CF.CreateBlockInfo(LEVEL_ID))


@ModBlockEntityRemoveClientEvent.Listen()
def on_fan_removed(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    if event.blockName == Machinery.INDUSTRIAL_FAN:
        loaded_fans.pop((event.dimensionId, event.posX, event.posY, event.posZ), None)


@ClientInitCallback()
@Repeat(0.1)
def update_fans():
    if not loaded_fans:
        return
    dimension = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    for key in tuple(loaded_fans):
        if key[0] == dimension:
            update_fan(key, block_info)


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(event):
    # type: (DimensionChangeClientEvent) -> None
    for key in tuple(loaded_fans):
        if key[0] == event.fromDimensionId:
            loaded_fans.pop(key, None)


@ClientUninitCallback()
def on_client_uninit():
    loaded_fans.clear()
