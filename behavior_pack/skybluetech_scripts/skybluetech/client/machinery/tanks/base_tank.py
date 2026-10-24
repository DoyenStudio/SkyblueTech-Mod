# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import Repeat
from skybluetech_scripts.skybluetech.common.define.id_enum import Tank
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)

from ...utils.fluid_model import FluidModel

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
    blockEntityData = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData((x, y, z))
    if blockEntityData is None:
        return
    max_volume = TANK_MAX_VOLUMES[event.blockName]
    fluid_id, _, _ = getFluidDataFromBlock(blockEntityData, max_volume)
    client_tank_datas[(x, y, z)] = (None, -1, max_volume)
    if fluid_id is not None:
        loadModel(
            x, y, z, prevent_duplicated=True
        )  # 客户端实体在切换维度时不会卸载, 但是会重新加载
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


def loadModel(x, y, z, prevent_duplicated=False):
    # type: (int, int, int, bool) -> FluidModel
    if (x, y, z) in client_models:
        if not prevent_duplicated:
            return client_models[(x, y, z)]
        else:
            client_models.pop((x, y, z)).Destroy()
    model = FluidModel(x, y, z)
    client_models[(x, y, z)] = model
    return model


def getFluidDataFromBlock(block_entity_data, max_volume):
    # type: (dict, float) -> tuple[str | None, float, float]
    fluid = FluidSlotClient(block_entity_data["exData"], 0, max_volume)
    return fluid.fluid_id, fluid.volume, max_volume


def getModelScaleRel(fluid_volume, max_volume):
    # type: (float, float) -> float
    if fluid_volume is None:
        return 0
    if fluid_volume == INFINITY:
        return 1
    elif max_volume == INFINITY:
        return 0
    elif not max_volume:
        # max_volume 为 0 或 None, 避免除零
        return 2
    else:
        return fluid_volume * 1.0 / max_volume


def updateClientTanksOnce():
    for (x, y, z), (
        old_fluid_id,
        old_fluid_volume,
        max_volume,
    ) in client_tank_datas.copy().items():
        blockdata = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData((x, y, z))
        if blockdata is None:
            # TODO: BUG: 切换维度不触发
            # print("[ERROR] Tank: BlockEntityData is None")
            continue
        fluid_id, fluid_volume, max_volume = getFluidDataFromBlock(blockdata, max_volume)
        vol_pc = getModelScaleRel(fluid_volume, max_volume)
        # sync_modify 表示"本次涉及的模型操作均未失败", 初值为 True;
        # 仅当某次贴图/液面设置失败(模型尚未就绪)时置 False, 不更新缓存以便下次重试。
        sync_modify = True
        if fluid_id != old_fluid_id:
            if old_fluid_id is None and fluid_id is not None:
                sync_modify = loadModel(x, y, z).SetTexture(fluid_id)
            elif old_fluid_id is not None and fluid_id is None:
                client_models.pop((x, y, z)).Destroy()
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
