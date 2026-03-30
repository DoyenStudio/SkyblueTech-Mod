# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .register import RegisterCommand


@RegisterCommand("skybluetech:query_transmitter_networks")
def onCommand(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    from ..transmitters import cable, pipe, wire

    ret = "Transmitter networks:\n\tCable: %d\n\tPipe: %d\n\tWire: %d" % (
        len(cable.logic.logic_module.networks_pool),
        len(pipe.logic.logic_module.networks_pool),
        len(wire.logic.logic_module.networks_pool),
    )
    event.SetReturnMsg(ret)
