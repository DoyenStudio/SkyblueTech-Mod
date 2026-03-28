# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockName, NotifyOneMessage
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .utils import generate_simple_arg_mapping


@CustomCommandTriggerServerEvent.Listen()
def onCustomCommandTrigger(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    if event.command == "skybluetech:query_deepslate_lava_storage":
        from ..machinery.bedrock_lava_drill.lava_storage import (
            get_available_lava_storage,
        )

        args = generate_simple_arg_mapping(event.args)
        x = args["x"]
        z = args["z"]
        dim = event.origin["dimension"]
        if x is None or z is None:
            x, _, z = event.origin["blockPos"]
            if x is None or z is None:
                return
        x = int(x)
        z = int(z)
        # TODO: BUG: 世界外方块判定为 air
        if GetBlockName(dim, (x, 0, z)) is None:
            event.SetReturnMsg("commands.generic.outOfWorld")
            event.SetReturnFailed()
            return
        storage_left, storage_total = get_available_lava_storage(x, z)
        event.SetReturnMsg("%commands.skybluetech.query_deepslate_storage.success")
        event.SetReturnParams(str(storage_left), str(storage_total))
