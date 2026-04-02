# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.api.common import Repeat
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import (
    GeometryModel,
    CreateBlankModel,
)
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault
from ...common.define.id_enum.machinery import HYDROPONIC_BED as MACHINE_ID
from ...common.machinery_def.hydroponic_bed import K_CROP_ID, K_GROW_STAGE
from .utils.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

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


def update_single_hydroponic_bed(x, y, z, model):
    # type: (int, int, int, GeometryModel) -> None
    block_nbt = GetBlockEntityData(x, y, z) or {}
    ex_data = block_nbt.get("exData")
    if ex_data is None:
        return
    crop_id = GetValueWithDefault(ex_data, K_CROP_ID, None)
    grow_stage = GetValueWithDefault(ex_data, K_GROW_STAGE, 0)
    if crop_id == 2:
        crop_id = None
    if not crop_id:
        model.SetBlockModel("minecraft:air", 0)
    else:
        model.SetBlockModel(crop_id, grow_stage, (0.8, 0.8, 0.8))


@ClientInitCallback()
@Repeat(1)
def onClientInit():
    for (x, y, z), model in loaded_models.items():
        update_single_hydroponic_bed(x, y, z, model)
