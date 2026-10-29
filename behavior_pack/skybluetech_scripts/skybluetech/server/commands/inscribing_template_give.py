# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .register import RegisterCommand
from .utils import generate_simple_arg_mapping


@RegisterCommand("skybluetech:inscribing_template_give")
def onCommand(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    from ..misc.inscribing_template import GenerateInscribingTemplateByItemId

    player_id = event.origin.get("entityId")
    if player_id is None:
        event.SetReturnMsg("%commands.generic.noTargetMatch")
        return
    args = generate_simple_arg_mapping(event.args)
    item_id = args["templateItem"]["itemName"]
    CF.CreateItem(LEVEL_ID).SpawnItemToPlayerInv(
        GenerateInscribingTemplateByItemId(item_id).marshal(),
        player_id,
    )
    event.SetReturnMsg("%commands.skybluetech.inscribing_template_give.success")
