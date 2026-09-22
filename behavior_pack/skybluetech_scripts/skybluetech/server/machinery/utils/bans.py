# coding=utf-8
from mod.server.extraServerApi import GetLevelId

from skybluetech_scripts.tooldelta.api.server import (
    GetExtraData,
    SetExtraData,
    SetOnePopupNotice,
)
from skybluetech_scripts.tooldelta.define import Item
from ....common.events.machinery.bans import MachineBanListRequest, MachineBanListUpdate

K_BANNED_MACHINES = "skybluetech:banned_machines"


def is_machine_banned(machine_id):
    # type: (str) -> bool
    return machine_id in GetExtraData(GetLevelId(), K_BANNED_MACHINES, [])


def set_machine_banned(machine_id, banned):
    # type: (str, bool) -> bool
    machine_ids = set(GetExtraData(GetLevelId(), K_BANNED_MACHINES, []))
    if banned:
        machine_ids.add(machine_id)
    else:
        machine_ids.discard(machine_id)
    machine_ids = sorted(machine_ids)
    if not SetExtraData(GetLevelId(), K_BANNED_MACHINES, machine_ids):
        return False
    MachineBanListUpdate(machine_ids).sendAll()
    return True


@MachineBanListRequest.Listen()
def on_machine_ban_list_request(event):
    # type: (MachineBanListRequest) -> None
    MachineBanListUpdate(
        GetExtraData(GetLevelId(), K_BANNED_MACHINES, [])
    ).send(event.player_id)


def reject_banned_machine(player_id, machine_id):
    # type: (str, str) -> bool
    if not is_machine_banned(machine_id):
        return False
    item = Item(machine_id)
    SetOnePopupNotice(player_id, "§c该机器已被管理员禁用： %s" % item.GetBasicInfo().itemName)
    return True
