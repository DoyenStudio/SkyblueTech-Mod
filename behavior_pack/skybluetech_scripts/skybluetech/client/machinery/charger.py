# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client import (
    GetPlayerDimensionId as CGetPlayerDim,
    CreateDropItemModelEntity,
    SetDropItemTransform,
    DeleteClientDropItemEntity,
)
from skybluetech_scripts.tooldelta.events.notify import NotifyToServer
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from ...common.define.id_enum.machinery import CHARGER as MACHINE_ID
from ...common.events.machinery.charger import (
    ChargerItemModelUpdate,
    ChargeItemModelRequest,
)
from ...common.machinery.utils.block_sync import BlockSync
from .utils.mod_block_event import asModBlockRemovedListener, asModBlockLoadedListener

block_sync = BlockSync(MACHINE_ID)


cli_loading_machines = set()  # type: set[tuple[int, int, int]]
cli_models = {}  # type: dict[tuple[int, int, int], str]


@ChargerItemModelUpdate.Listen()
def onModelUpdate(event):
    # type: (ChargerItemModelUpdate) -> None
    pos = (event.x, event.y, event.z)
    if pos not in cli_loading_machines:
        return
    model_id = cli_models.get(pos)
    if model_id is not None:
        DeleteClientDropItemEntity(model_id)
    if event.item_id is not None:
        model_id = cli_models[pos] = CreateDropItemModelEntity(
            CGetPlayerDim(), pos, Item(event.item_id)
        )
        SetDropItemTransform(
            model_id, (event.x + 0.4, event.y + 0.5, event.z + 0.3), (90, 0, 0)
        )


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    cli_loading_machines.add(pos)
    # item_id
    NotifyToServer(ChargeItemModelRequest(event.posX, event.posY, event.posZ))


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    cli_loading_machines.discard(pos)
    model_id = cli_models.get(pos)
    if model_id is not None:
        DeleteClientDropItemEntity(cli_models.pop(pos))
