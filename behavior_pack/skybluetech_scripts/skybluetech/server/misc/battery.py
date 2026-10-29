# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.events.server import ServerItemTryUseEvent
from ..player.pool import GetPlayer
from ..machinery.utils.charge import CanChargeInventory, IsEnableCharge, SetEnableCharge


@ServerItemTryUseEvent.Listen()
def onUseItem(event):
    # type: (ServerItemTryUseEvent) -> None
    if not CF.CreatePlayer(event.playerId).isSneaking():
        return
    elif not CanChargeInventory(event.item):
        return
    prev_stat = IsEnableCharge(event.item)
    SetEnableCharge(event.item, not prev_stat)
    CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
        event.playerId,
        "§7[§f!§7] §e电池物品栏充模式： " + ("§a启用" if not prev_stat else "§c禁用"),
        "§6提示§f",
    )
    CF.CreateItem(event.playerId).SpawnItemToPlayerCarried(event.item.marshal(), event.playerId)
    if not prev_stat:
        player = GetPlayer(event.playerId)
        if player is None:
            return
        player.charge.enable_charge()
