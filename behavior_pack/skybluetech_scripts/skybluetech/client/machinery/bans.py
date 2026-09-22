# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import UiInitFinishedEvent

from ...common.events.machinery.bans import MachineBanListRequest, MachineBanListUpdate

banned_machine_ids = set()  # type: set[str]


def is_machine_banned(machine_id):
    # type: (str | None) -> bool
    return machine_id in banned_machine_ids


@MachineBanListUpdate.Listen()
def on_machine_ban_list_update(event):
    # type: (MachineBanListUpdate) -> None
    banned_machine_ids.clear()
    banned_machine_ids.update(event.machine_ids)


@UiInitFinishedEvent.Listen()
def on_ui_init_finished(_):
    banned_machine_ids.clear()
    MachineBanListRequest().send()
