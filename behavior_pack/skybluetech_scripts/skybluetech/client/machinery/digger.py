# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    UiInitFinishedEvent,
)
from skybluetech_scripts.tooldelta.api.client.block import (
    GetBlockNameAndAux as CGetBlockNameAndAux,
    GetBlockName,
    SetBlockEntityMolangValue,
    SetCrackFrame,
)
from ...common.events.machinery.digger import (
    DiggerWorkModeUpdatedEvent,
    DiggerUpdateCrack,
)
from ...common.define.id_enum.machinery import DIGGER as MACHINE_ID
from ...common.utils.block_sync import BlockSync

TICKS_PER_SECOND = 20
block_sync = BlockSync(MACHINE_ID)


@DiggerWorkModeUpdatedEvent.Listen()
def clientOnDiggerWorkModeUpdated(event):
    # type: (DiggerWorkModeUpdatedEvent) -> None
    SetBlockEntityMolangValue(
        (event.x, event.y, event.z), "variable.mod_block_is_active", event.active
    )


@ModBlockEntityLoadedClientEvent.Listen()
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    if event.blockName == MACHINE_ID:
        _, aux = CGetBlockNameAndAux((event.posX, event.posY, event.posZ))
        SetBlockEntityMolangValue(
            (event.posX, event.posY, event.posZ),
            "variable.mod_block_facing",
            aux & 0b111,
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
    if not GetBlockName((event.x, event.y, event.z)):
        # Digger crack was too early to set, may crash game
        return
    if can_play_animation:
        SetCrackFrame(event.dim, (event.x, event.y, event.z), event.level)
