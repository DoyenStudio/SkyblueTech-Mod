# coding=utf-8
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
    DimensionChangeClientEvent,
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import ClientUninitCallback

from ....common.define.id_enum import Machinery
from ....common.utils.block_sync import BlockSync

block_sync = BlockSync(Machinery.TESLA_PLANT, side=BlockSync.SIDE_CLIENT)
model_entities = {}  # type: dict[tuple[int, int, int, int], str]


def get_layer(x, y, z):
    # Tesla has exactly one block state: skybluetech:layer = 0, 1, 2.
    _, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock((x, y, z)) or (None, 0)
    return aux & 3


def remove_model(pos):
    entity_id = model_entities.pop(pos, None)
    if entity_id is not None:
        GetClient().DestroyClientEntity(entity_id)


def clear_models():
    for pos in list(model_entities):
        remove_model(pos)


@ClientBlockUseEvent.Listen(priority=10)
def on_tesla_plant_use(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName != Machinery.TESLA_PLANT:
        return
    layer = get_layer(event.x, event.y, event.z)
    if layer == 0:
        return
    base_y = event.y - layer
    base_name, base_aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock(
        (event.x, base_y, event.z)
    ) or (None, 0)
    if base_name != Machinery.TESLA_PLANT or base_aux & 3:
        return
    event.y = base_y
    event.aux = base_aux
    # Each ToolDelta priority builds a new event from the native dictionary.
    # GUIControl's client proxy records its binding at priority 0.
    event._orig["y"] = base_y
    event._orig["aux"] = base_aux


@asModBlockLoadedListener(Machinery.TESLA_PLANT)
def on_tesla_plant_loaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.dimensionId != CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension():
        return
    pos = (event.posX, event.posY, event.posZ)
    if get_layer(*pos) != 0:
        return
    key = (event.dimensionId,) + pos
    remove_model(key)
    # The supplied model is centered at (0, 0, 0), unlike WindGenerator's
    # model which already includes its half-block placement offset.
    entity_id = GetClient().CreateClientEntityByTypeStr(
        "skybluetech:tesla_plant_model",
        (event.posX + 0.5, event.posY, event.posZ + 0.5),
        (0, 0),
    )
    if entity_id is not None:
        model_entities[key] = entity_id
        CF.CreateModel(entity_id).SetEntityShadowShow(False)


@asModBlockRemovedListener(Machinery.TESLA_PLANT)
def on_tesla_plant_removed(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    remove_model((event.dimensionId, event.posX, event.posY, event.posZ))


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(_):
    clear_models()


@ClientUninitCallback()
def on_client_exit():
    clear_models()
