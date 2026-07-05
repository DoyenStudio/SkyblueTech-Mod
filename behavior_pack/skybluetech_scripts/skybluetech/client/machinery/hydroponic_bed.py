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
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.HYDROPONIC_BED
from ...common.machinery_def.hydroponic_bed import K_CROP_BLOCK_ID, K_GROW_STAGE
from .utils.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

loaded_models = {}  # type: dict[tuple[int, int, int], GeometryModel]


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if (event.posX, event.posY, event.posZ) in loaded_models:
        loaded_models.pop((event.posX, event.posY, event.posZ)).Destroy()
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
    # type: (int, int, int, GeometryModel) -> bool
    block_nbt = GetBlockEntityData(x, y, z) or {}
    ex_data = block_nbt.get("exData")
    if ex_data is None:
        return False
    crop_block_id = GetValueWithDefault(ex_data, K_CROP_BLOCK_ID, None)
    grow_stage = GetValueWithDefault(ex_data, K_GROW_STAGE, 0)
    if crop_block_id == 2:
        crop_block_id = None
    if not crop_block_id:
        ok = model.SetBlockModel("minecraft:air", 0)
    else:
        ok = model.SetBlockModel(crop_block_id, grow_stage, (0.8, 0.8, 0.8))
    return ok


@ClientInitCallback()
@Repeat(1)
def onClientInit():
    for (x, y, z), model in loaded_models.items():
        ok = update_single_hydroponic_bed(x, y, z, model)
        if not ok:
            model.Destroy()
            del loaded_models[(x, y, z)]
            break
