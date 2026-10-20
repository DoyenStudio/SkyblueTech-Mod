# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .register import RegisterCommand


@RegisterCommand("skybluetech:query_transmitter_networks")
def onCommand(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    from ..transmitters import item_pipe, fluid_pipe, wire

    ret = "Transmitter networks:\n\tItemPipe: %d\n\tFluidPipe: %d\n\tWire: %d" % (
        len(item_pipe.logic.logic_module.networks_pool),
        len(fluid_pipe.logic.logic_module.networks_pool),
        len(wire.logic.logic_module.networks_pool),
    )
    event.SetReturnMsg(ret)
