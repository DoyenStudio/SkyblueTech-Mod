# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.utils.timer import Delay
from mod_log import logger
from ...common.events.misc.block_geometry_test import BlockGeometryTest


@BlockGeometryTest.Listen()
def onRecvTest(event):
    # type: (BlockGeometryTest) -> None
    pal = CF.CreateBlock(LEVEL_ID).GetBlockPaletteBetweenPos(
        event.start_pos,
        event.end_pos,
        eliminateAir=False,
    )
    geo_id = CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
        pal,
        'geometry.block_geometry.test',
    )
    entity_id = GetClient().CreateClientEntityByTypeStr('skybluetech:model_entity', event.display_pos, (0, 0))
    if entity_id is not None:
        res = CF.CreateActorRender(entity_id).AddActorBlockGeometry(geo_id, (0, 0, 0), (0, 180, 0))
        remove_later(entity_id)
        if not res:
            logger.error("AddActorBlockGeometry failed")
    else:
        logger.error("CreateClientEntity failed")


@Delay(30)
def remove_later(entity_id):
    # type: (str) -> None
    GetClient().DestroyClientEntity(entity_id)
