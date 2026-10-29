# coding=utf-8
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent
from skybluetech_scripts.tooldelta.extensions.mod_block_event import asModBlockRemovedListener
from skybluetech_scripts.tooldelta.general import ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ....common.define.id_enum import Machinery
from ....common.machinery_def.tesla_plant import MIN_WORK_RANGE, MAX_WORK_RANGE

PREVIEW_SECONDS = 8
FRAME_WIDTH = 0.25


class RangePreview(object):
    def __init__(self):
        self.entity_id = None
        self.block_pos = None

    def start(self, dim, x, y, z, work_range):
        # type: (int, int, int, int, int) -> bool
        if dim != CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension():
            return False
        if type(work_range) is not int or not MIN_WORK_RANGE <= work_range <= MAX_WORK_RANGE:
            return False
        self.finish()
        entity_id = GetClient().CreateClientEntityByTypeStr(
            "skybluetech:tesla_range_preview", (x + 0.5, y + 2.5, z + 0.5), (0, 0)
        )
        if not entity_id:
            return False
        radius = float(work_range)
        if not CF.CreateActorRender(entity_id).SetEntityExtraUniforms(
            1, (radius, radius, radius, FRAME_WIDTH)
        ):
            GetClient().DestroyClientEntity(entity_id)
            return False
        self.entity_id = entity_id
        self.block_pos = (dim, x, y, z)
        CF.CreateModel(entity_id).SetEntityShadowShow(False)
        # An old preview's timeout must never remove a replacement entity.
        ExecLater(PREVIEW_SECONDS, self.finish, entity_id)
        return True

    def finish(self, entity_id=None):
        if entity_id is not None and entity_id != self.entity_id:
            return
        if self.entity_id is not None:
            GetClient().DestroyClientEntity(self.entity_id)
            self.entity_id = None
        self.block_pos = None


range_preview = RangePreview()


def start_preview(dim, x, y, z, work_range):
    # type: (int, int, int, int, int) -> bool
    return range_preview.start(dim, x, y, z, work_range)


@asModBlockRemovedListener(Machinery.TESLA_PLANT)
def on_tesla_plant_removed(event):
    if range_preview.block_pos is None:
        return
    dim, x, y, z = range_preview.block_pos
    if (
        event.dimensionId == dim and event.posX == x and event.posZ == z
        and y <= event.posY <= y + 2
    ):
        range_preview.finish()


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(_):
    range_preview.finish()


@ClientUninitCallback()
def on_client_uninit():
    range_preview.finish()
