# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient

from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

from ...common.define.id_enum import TransmitBelt
from ..utils.client_molangs import TRANSMIT_BELT_STATE

client_entities_pool = {}  # type: dict[tuple[int, int, int, int], str]


@asModBlockLoadedListener(TransmitBelt.BELT)
@asModBlockLoadedListener(TransmitBelt.EXTRACTOR)
@asModBlockLoadedListener(TransmitBelt.INSERTER)
def onTransmitBeltLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    _, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock((event.posX, event.posY, event.posZ)) or (None, 0)
    facing = aux & 0b11
    entity_type = {
        TransmitBelt.BELT: "skybluetech:transmit_belt_entity",
        TransmitBelt.EXTRACTOR: "skybluetech:extractor_belt_entity",
        TransmitBelt.INSERTER: "skybluetech:inserter_belt_entity",
    }[event.blockName]
    eid = GetClient().CreateClientEntityByTypeStr(
        entity_type,
        (event.posX + 0.5, event.posY, event.posZ + 0.5),
        (0, 180 + facing * 90),
    )
    if eid is None:
        return
    CF.CreateModel(eid).SetEntityShadowShow(False)
    TRANSMIT_BELT_STATE.set_to_entity(eid, (aux & 0b11100) >> 2)
    client_entities_pool[(event.dimensionId, event.posX, event.posY, event.posZ)] = eid


@asModBlockRemovedListener(TransmitBelt.BELT)
@asModBlockRemovedListener(TransmitBelt.EXTRACTOR)
@asModBlockRemovedListener(TransmitBelt.INSERTER)
def onTransmitBeltRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    eid = client_entities_pool.pop((event.dimensionId, event.posX, event.posY, event.posZ), None)
    if eid is None:
        return
    GetClient().DestroyClientEntity(eid)
