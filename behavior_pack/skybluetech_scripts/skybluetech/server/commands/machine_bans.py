# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent

from .register import RegisterCommand
from .utils import generate_simple_arg_mapping


@RegisterCommand("skybluetech:ban_machine")
@RegisterCommand("skybluetech:unban_machine")
def on_machine_ban_command(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    from ..machinery.core.registry import registered_machines
    from ..machinery.utils.bans import set_machine_banned

    args = generate_simple_arg_mapping(event.args)
    machine_arg = args.get("machineId", {})
    machine_id = (
        machine_arg.get("itemName", "")
        if isinstance(machine_arg, dict)
        else machine_arg
    )
    if machine_id not in registered_machines:
        event.SetReturnMsg("%commands.skybluetech.machine_bans.invalid_machine")
        event.SetReturnParams(str(machine_id))
        event.SetReturnFailed()
        return
    banned = event.command == "skybluetech:ban_machine"
    if not set_machine_banned(machine_id, banned):
        event.SetReturnMsg("%commands.skybluetech.machine_bans.save_failed")
        event.SetReturnFailed()
        return
    event.SetReturnMsg(
        "%commands.skybluetech.ban_machine.success"
        if banned
        else "%commands.skybluetech.unban_machine.success"
    )
    event.SetReturnParams(machine_id)
