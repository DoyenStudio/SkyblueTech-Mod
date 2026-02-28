# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetPosBlockTags, SetBlock
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.events.server import PistonActionServerEvent


@PistonActionServerEvent.Listen()
def onPistonAction(event):
    # type: (PistonActionServerEvent) -> None
    for x, y, z in event.blockList:
        if "piston_denier" in (GetPosBlockTags(event.dimensionId, (x, y, z)) or ()):
            event.cancel()
            removePistonLater(event)
            break


@Delay(0)
def removePistonLater(event):
    # type: (PistonActionServerEvent) -> None
    SetBlock(
        event.dimensionId,
        (event.pistonX, event.pistonY, event.pistonZ),
        "minecraft:air",
        old_block_handing=1,
    )
