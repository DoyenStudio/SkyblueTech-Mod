# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
#
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    UiInitFinishedEvent,
)

from ...common.define.id_enum import Machinery
from ...common.events.machinery.digger import (
    DiggerUpdateCrack,
    DiggerWorkModeUpdatedEvent,
)
from ...common.utils.block_sync import BlockSync

TICKS_PER_SECOND = 20
block_sync = BlockSync(Machinery.DIGGER, side=BlockSync.SIDE_CLIENT)

ROTATION_VALUES = {
    0: (0, 0),
    1: (180,  0),
    2: (-90,  90),
    3: (90,  -90),
    4: (0,  -90),
    5: (0,  90),
}


@DiggerWorkModeUpdatedEvent.Listen()
def clientOnDiggerWorkModeUpdated(event):
    # type: (DiggerWorkModeUpdatedEvent) -> None
    CF.CreateBlockInfo(LEVEL_ID).SetBlockEntityMolangValue(
        (event.x, event.y, event.z),
        'variable.working',
        event.active,
    )


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName == Machinery.DIGGER:
        _, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock((event.posX, event.posY, event.posZ)) or (None, 0)
        rot_x, rot_z = ROTATION_VALUES[aux & 0b111]
        CF.CreateBlockInfo(LEVEL_ID).SetBlockEntityMolangValue(
            (event.posX, event.posY, event.posZ),
            'variable.rotation_x',
            rot_x,
        )
        CF.CreateBlockInfo(LEVEL_ID).SetBlockEntityMolangValue(
            (event.posX, event.posY, event.posZ),
            'variable.rotation_z',
            rot_z,
        )


can_play_animation = False


@UiInitFinishedEvent.Listen()
def onUIInitFinished(event):
    # type: (UiInitFinishedEvent) -> None
    global can_play_animation
    can_play_animation = True


@DiggerUpdateCrack.Listen()
def onUpdateCrack(event):
    # type: (DiggerUpdateCrack) -> None
    # WARNING: 调用不当将导致游戏强制中断
    global can_play_animation
    if not (CF.CreateBlockInfo(LEVEL_ID).GetBlock((event.x, event.y, event.z)) or (None, 0))[0]:
        # Digger crack was too early to set, may crash game
        return
    if can_play_animation:
        CF.CreateBlockInfo(LEVEL_ID).SetCrackFrame(event.dim, (event.x, event.y, event.z), event.level)
