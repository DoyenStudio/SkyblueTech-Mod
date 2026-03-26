# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import (
    GeometryModel,
    CreateBlankModel,
)
from ...common.events.machinery.hydroponic_bed import (
    HydroponicBedModelUpdateEvent,
    HydroponicBedModelUpdatesEvent,
)
from ...common.define.id_enum.machinery import HYDROPONIC_BED as MACHINE_ID
from ...common.utils.block_sync import BlockSync
from .utils.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_CLIENT)
loaded_models = {}  # type: dict[tuple[int, int, int], GeometryModel]


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    loaded_models[(event.posX, event.posY, event.posZ)] = CreateBlankModel((
        event.posX,
        event.posY + 3.0 / 16 * 0.4,
        event.posZ,
    ))


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    model = loaded_models.pop((event.posX, event.posY, event.posZ), None)
    if model is not None:
        model.Destroy()


@HydroponicBedModelUpdateEvent.Listen()
def onS2CUpdate(event):
    # type: (HydroponicBedModelUpdateEvent) -> None
    key = (event.x, event.y, event.z)
    if event.crop_id is None:
        model = loaded_models.get(key, None)
        if model is not None:
            model.SetBlockModel("minecraft:air", 0)
    elif event.crop_id is not None:
        model = loaded_models.get(key)
        if model is not None:
            model.SetBlockModel(event.crop_id, event.aux, (0.8, 0.8, 0.8))
