# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
import time

from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

from ...common.define.id_enum import TransmitBelt
from ..utils.client_molangs import TIME_OFFSET, TRANSMIT_BELT_STATE

client_entities_pool = {}  # type: dict[tuple[int, int, int], str]


@asModBlockLoadedListener(TransmitBelt.BELT)
def onTransmitBeltLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    _, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock((event.posX, event.posY, event.posZ)) or (None, 0)
    facing = aux & 0b11
    eid = GetClient().CreateClientEntityByTypeStr(
        'skybluetech:transmit_belt_entity',
        (event.posX + 0.5, event.posY, event.posZ + 0.5),
        (0, 180 + facing * 90),
    )
    if eid is None:
        return
    TIME_OFFSET.set_to_entity(eid, time.time() % 86400)
    CF.CreateModel(eid).SetEntityShadowShow(False)
    TRANSMIT_BELT_STATE.set_to_entity(eid, (aux & 0b11100) >> 2)
    client_entities_pool[(event.posX, event.posY, event.posZ)] = eid


@asModBlockRemovedListener(TransmitBelt.BELT)
def onTransmitBeltRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    eid = client_entities_pool.pop((event.posX, event.posY, event.posZ), None)
    if eid is None:
        return
    GetClient().DestroyClientEntity(eid)
