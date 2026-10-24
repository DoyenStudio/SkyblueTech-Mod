# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.define import Item
from ....common.events.machinery.bans import MachineBanListRequest, MachineBanListUpdate

K_BANNED_MACHINES = "skybluetech:banned_machines"


def is_machine_banned(machine_id):
    # type: (str) -> bool
    machine_ids = CF.CreateExtraData(LEVEL_ID).GetExtraData(K_BANNED_MACHINES)
    return machine_id in (machine_ids if machine_ids is not None else [])


def set_machine_banned(machine_id, banned):
    # type: (str, bool) -> bool
    saved_ids = CF.CreateExtraData(LEVEL_ID).GetExtraData(K_BANNED_MACHINES)
    machine_ids = set(saved_ids if saved_ids is not None else [])
    if banned:
        machine_ids.add(machine_id)
    else:
        machine_ids.discard(machine_id)
    machine_ids = sorted(machine_ids)
    if not CF.CreateExtraData(LEVEL_ID).SetExtraData(K_BANNED_MACHINES, machine_ids, True):
        return False
    MachineBanListUpdate(machine_ids).sendAll()
    return True


@MachineBanListRequest.Listen()
def on_machine_ban_list_request(event):
    # type: (MachineBanListRequest) -> None
    machine_ids = CF.CreateExtraData(LEVEL_ID).GetExtraData(K_BANNED_MACHINES)
    MachineBanListUpdate(machine_ids if machine_ids is not None else []).send(event.player_id)


def reject_banned_machine(player_id, machine_id):
    # type: (str, str) -> bool
    if not is_machine_banned(machine_id):
        return False
    item = Item(machine_id)
    CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
        player_id,
        "§c该机器已被管理员禁用： %s" % item.GetBasicInfo().itemName,
        "§6提示§f",
    )
    return True
