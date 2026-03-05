# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetLocalPlayerMainhandItem
from skybluetech_scripts.tooldelta.events.client import StartDestroyBlockClientEvent
from ...common.define.id_enum.items import METAL_HAMMER


@StartDestroyBlockClientEvent.Listen()
def onStartDestroyBlock(event):
    # type: (StartDestroyBlockClientEvent) -> None
    mhitem = GetLocalPlayerMainhandItem()
    if mhitem is None or mhitem.id != METAL_HAMMER:
        return
    event.cancel()
