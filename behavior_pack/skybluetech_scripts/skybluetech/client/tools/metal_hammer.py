# coding=utf-8
from mod.client.extraClientApi import GetLocalPlayerId, GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.cli import CF
from skybluetech_scripts.tooldelta.events.client import StartDestroyBlockClientEvent
from ...common.define.id_enum.items import METAL_HAMMER


@StartDestroyBlockClientEvent.Listen()
def onStartDestroyBlock(event):
    # type: (StartDestroyBlockClientEvent) -> None
    mhitem_data = CF.CreateItem(GetLocalPlayerId()).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED, 0, True
    )
    mhitem = Item.from_dict(mhitem_data) if mhitem_data is not None else None
    if mhitem is None or mhitem.id != METAL_HAMMER:
        return
    event.cancel()
