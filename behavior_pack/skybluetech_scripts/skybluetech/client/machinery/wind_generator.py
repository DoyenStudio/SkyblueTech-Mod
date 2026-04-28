# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    ClientBlockUseEvent,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockNameAndAux,
    CreateClientEntity,
    DestroyClientEntity,
    AddTextureToOneActor,
    RebuildRenderForOneActor,
    SetEntityShadowShow,
)
from ...common.events.machinery.wind_generator import (
    WindGeneratorStatesRequest,
    WindGeneratorStatesUpdate,
)
from ...common.define.id_enum.machinery import WIND_GENERATOR as MACHINE_ID
from ...common.utils.block_sync import BlockSync
from .utils.client_molangs import (
    FACE,
    ANIM_SPEED,
    IS_BASE_BLOCK,
    WIRE_CONNECT_EAST,
    WIRE_CONNECT_NORTH,
    WIRE_CONNECT_SOUTH,
    WIRE_CONNECT_WEST,
)
from .utils.mod_block_event import asModBlockLoadedListener, asModBlockRemovedListener

PaddleEnum = WindGeneratorStatesUpdate

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_CLIENT)


def get_layer(x, y, z):
    # type: (int, int, int) -> int
    _, aux = GetBlockNameAndAux((x, y, z))
    return (aux & 0b1100) >> 2


def update_wind_generator_render(entity_id, x, y, z, paddle_type):
    # type: (str, int, int, int, int | None) -> None
    _, aux = GetBlockNameAndAux((x, y, z))
    facing = aux & 0b11
    layer = (aux & 0b1100) >> 2
    is_conn_east = bool(aux & 0b00010000)
    is_conn_north = bool(aux & 0b00100000)
    is_conn_south = bool(aux & 0b01000000)
    is_conn_west = bool(aux & 0b10000000)
    if layer != 0:
        return

    if paddle_type is not None:
        texture = {
            PaddleEnum.PADDLE_EMPTY: "textures/models/wind_generator_empty_texture",
            PaddleEnum.PADDLE_IRON: "textures/models/wind_generator_ironpaddle_texture",
            PaddleEnum.PADDLE_STEEL: "textures/models/wind_generator_steelpaddle_texture",
        }.get(paddle_type, "textures/models/wind_generator_empty_texture")
        AddTextureToOneActor(entity_id, "default", texture)
        RebuildRenderForOneActor(entity_id)

    IS_BASE_BLOCK.set_to_entity(entity_id, 1)
    FACE.set_to_entity(entity_id, facing)
    WIRE_CONNECT_EAST.set_to_entity(entity_id, float(is_conn_east))
    WIRE_CONNECT_SOUTH.set_to_entity(entity_id, float(is_conn_south))
    WIRE_CONNECT_NORTH.set_to_entity(entity_id, float(is_conn_north))
    WIRE_CONNECT_WEST.set_to_entity(entity_id, float(is_conn_west))


client_modelentity_pool = {}  # type: dict[tuple[int, int, int], str]


def create_model_entity(x, y, z):
    # type: (int, int, int) -> str
    res = CreateClientEntity("skybluetech:wind_generator_model", (x, y, z), (0, 0))
    if res is None:
        raise ValueError("WindGenerator error: Create ModelEntity failed")
    old = client_modelentity_pool.pop((x, y, z), None)
    if old is not None:
        destroy_model_entity(x, y, z)
    client_modelentity_pool[(x, y, z)] = res
    SetEntityShadowShow(res, False)
    return res


def destroy_model_entity(x, y, z):
    # type: (int, int, int) -> None
    entity_id = client_modelentity_pool.pop((x, y, z), None)
    if entity_id is not None:
        DestroyClientEntity(entity_id)


@ClientBlockUseEvent.Listen(inner_priority=10)
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName != MACHINE_ID:
        return
    _, aux = GetBlockNameAndAux((event.x, event.y, event.z))
    layer = (aux & 0b1100) >> 2
    if layer != 0:
        # 只改变 GUI 读取到的 xyz。。
        event.y -= layer


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    layer = get_layer(event.posX, event.posY, event.posZ)
    if layer != 0:
        return
    entity_id = create_model_entity(event.posX, event.posY, event.posZ)
    update_wind_generator_render(entity_id, event.posX, event.posY, event.posZ, None)
    WindGeneratorStatesRequest(event.posX, event.posY, event.posZ).send()


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    destroy_model_entity(event.posX, event.posY, event.posZ)


@WindGeneratorStatesUpdate.Listen()
def onStateUpdated(event):
    # type: (WindGeneratorStatesUpdate) -> None
    entity_id = client_modelentity_pool.get((event.x, event.y, event.z))
    if entity_id is None:
        return
    ANIM_SPEED.set_to_entity(entity_id, event.rot_speed)
    update_wind_generator_render(
        entity_id, event.x, event.y, event.z, event.paddle_type
    )
