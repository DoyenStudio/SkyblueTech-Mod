# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockName
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .register import RegisterCommand
from .utils import generate_simple_arg_mapping


@RegisterCommand("skybluetech:reset_deactive_flags")
def onCommand(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    from ..machinery.pool import GetMachineStrict

    args = generate_simple_arg_mapping(event.args)
    x, y, z = args["position"]
    if not isinstance(x, float) or not isinstance(y, float) or not isinstance(z, float):
        event.SetReturnMsg("Need position")
        event.SetReturnFailed()
        return
    x = int(x)
    y = int(y)
    z = int(z)
    m = GetMachineStrict(event.origin["dimension"], x, y, z)
    if m is None:
        event.SetReturnMsg("Not machine at %d %d %d" % (x, y, z))
        event.SetReturnFailed()
    else:
        m.ResetDeactiveFlags()
        event.SetReturnMsg("Reset deactive flags successfully.")
