# coding=utf-8
#
from skybluetech_scripts.tooldelta.api.common import Repeat
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.utils.nbt import GetValue
from ....common.define.id_enum import Tank
from ....common.machinery_def.fluid_container import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_VOLUME,
)
from ..utils.fluid_model import FluidModel

INFINITY = float("inf")
FIRST_TANK_LOADED = False


client_tank_datas = {}  # type: dict[tuple[int, int, int], tuple[str | None, float, float]]
client_models = {}  # type: dict[tuple[int, int, int], FluidModel]


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockEntityLoadedClientEvent(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    global FIRST_TANK_LOADED
    if event.blockName not in Tank.all():
        return
    x = event.posX
    y = event.posY
    z = event.posZ
    blockEntityData = GetBlockEntityData(x, y, z)
    if blockEntityData is None:
        raise Exception("BlockEntityData is None")
    fluid_id, _, max_volume = getFluidDataFromBlock(blockEntityData)
    client_tank_datas[(x, y, z)] = (None, -1, max_volume)
    if fluid_id is not None:
        loadModel(x, y, z)
    if not FIRST_TANK_LOADED:
        Repeat(0.2)(updateClientTanksOnce)()
        FIRST_TANK_LOADED = True
    else:
        updateClientTanksOnce()


@ModBlockEntityRemoveClientEvent.Listen()
def onModBlockEntityRemoveClientEvent(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    if event.blockName not in Tank.all():
        return
    x = event.posX
    y = event.posY
    z = event.posZ
    if (x, y, z) in client_models:
        client_models.pop((x, y, z)).Destroy()
    if (x, y, z) in client_tank_datas:
        client_tank_datas.pop((x, y, z))


def loadModel(x, y, z):
    # type: (int, int, int) -> FluidModel
    if (x, y, z) in client_models:
        return client_models[(x, y, z)]
    else:
        model = FluidModel(x, y, z)
        client_models[(x, y, z)] = model
        return model


def getFluidDataFromBlock(block_entity_data):
    # type: (dict) -> tuple[str | None, float, float]
    ex_data = block_entity_data["exData"]
    if K_FLUID_ID not in ex_data:
        return None, 0, 1
    fluid_id_datas = ex_data[K_FLUID_ID]
    if fluid_id_datas["__type__"] == 1:
        # None
        return (
            None,
            GetValue(ex_data, K_FLUID_VOLUME),
            GetValue(ex_data, K_MAX_VOLUME),
        )
    return (
        GetValue(ex_data, K_FLUID_ID),
        GetValue(ex_data, K_FLUID_VOLUME),
        GetValue(ex_data, K_MAX_VOLUME),
    )


def getModelScaleRel(fluid_volume, max_volume):
    # type: (float, float) -> float
    if fluid_volume == INFINITY:
        return 1
    elif max_volume == INFINITY:
        return 0
    elif max_volume == 0:
        return 2
    else:
        return fluid_volume / max_volume


def updateClientTanksOnce():
    for (x, y, z), (
        old_fluid_id,
        old_fluid_volume,
        _,
    ) in client_tank_datas.copy().items():
        blockdata = GetBlockEntityData(x, y, z)
        if blockdata is None:
            # TODO: BUG: 切换维度不触发
            # print("[ERROR] Tank: BlockEntityData is None")
            continue
        fluid_id, fluid_volume, max_volume = getFluidDataFromBlock(blockdata)
        if fluid_volume == INFINITY:
            vol_pc = 1
        elif max_volume == INFINITY:
            vol_pc = 0
        else:
            vol_pc = float(fluid_volume) / max_volume
        sync_modify = False
        if fluid_id != old_fluid_id:
            if old_fluid_id is None and fluid_id is not None:
                sync_modify = loadModel(x, y, z).SetTexture(fluid_id)
            elif old_fluid_id is not None and fluid_id is None:
                client_models.pop((x, y, z)).Destroy()
                sync_modify = True
            elif old_fluid_id is not None and fluid_id is not None:
                client_models.pop((x, y, z)).Destroy()
                sync_modify = loadModel(x, y, z).SetTexture(fluid_id)
        if fluid_id is not None and fluid_volume != old_fluid_volume:
            res = loadModel(x, y, z).SetYScale(vol_pc)
            sync_modify = sync_modify and res
        if sync_modify:
            # 只考虑模型加载失败, 即游戏未完全加载完成时,
            # 不同步更改, 使得下次仍然尝试加载模型
            client_tank_datas[(x, y, z)] = (fluid_id, fluid_volume, max_volume)
