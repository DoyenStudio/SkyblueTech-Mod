# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.utils.timer import Delay
from skybluetech_scripts.tooldelta.events.server import PistonActionServerEvent


@PistonActionServerEvent.Listen()
def onPistonAction(event):
    # type: (PistonActionServerEvent) -> None
    for x, y, z in event.blockList:
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew((x, y, z), event.dimensionId)
        if block is None:
            continue
        if "piston_denier" in CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(block["name"]):
            event.cancel()
            removePistonLater(event)
            break


@Delay(0)
def removePistonLater(event):
    # type: (PistonActionServerEvent) -> None
    CF.CreateBlockInfo(LEVEL_ID).SetBlockNew(
        (event.pistonX, event.pistonY, event.pistonZ),
        {"name": "minecraft:air", "aux": 0},
        1,
        dimensionId=event.dimensionId,
    )
