# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ClientBlockUseEvent,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockNameAndAux,
    SetBlockEntityMolangValue,
)
from ...common.events.machinery.wind_generator import (
    WindGeneratorStatesRequest,
    WindGeneratorStatesUpdate,
)
from ...common.define.id_enum.machinery import WIND_GENERATOR as MACHINE_ID
from ...common.machinery.utils.block_sync import BlockSync

block_sync = BlockSync(MACHINE_ID)


def update_wind_generator_render(x, y, z):
    # type: (int, int, int) -> None
    _, aux = GetBlockNameAndAux((x, y, z))
    facing = aux & 0b11
    layer = (aux & 0b1100) >> 2
    is_conn_west = bool(aux & 0b00010000)
    is_conn_south = bool(aux & 0b00100000)
    is_conn_north = bool(aux & 0b01000000)
    is_conn_east = bool(aux & 0b10000000)
    if layer != 0:
        return
    for molang_name, value in (
        ("variable.mod_is_base_block", 1),
        ("variable.mod_block_facing", facing),
        ("variable.is_connect_east", is_conn_east),
        ("variable.is_connect_south", is_conn_south),
        ("variable.is_connect_west", is_conn_west),
        ("variable.is_connect_north", is_conn_north),
    ):
        SetBlockEntityMolangValue(
            (x, y, z),
            molang_name,
            value,
        )


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


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName != MACHINE_ID:
        return
    update_wind_generator_render(event.posX, event.posY, event.posZ)
    WindGeneratorStatesRequest(event.posX, event.posY, event.posZ).send()


@WindGeneratorStatesUpdate.Listen()
def onStateUpdated(event):
    # type: (WindGeneratorStatesUpdate) -> None
    SetBlockEntityMolangValue(
        (event.x, event.y, event.z),
        "variable.mod_anim_speed",
        event.rot_speed,
    )
    update_wind_generator_render(event.x, event.y, event.z)
