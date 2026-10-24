# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum
from mod_log import logger
from skybluetech_scripts.tooldelta.define import Item

from skybluetech_scripts.tooldelta.events.server import (
    ServerItemTryUseEvent,
    PushUIRequest,
)
from skybluetech_scripts.tooldelta.utils import nbt
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.skybluetech.common.define.id_enum import INSCRIBING_TEMPLATE
from skybluetech_scripts.skybluetech.common.events.misc.inscribling_template import (
    InscribingTemplateGraphUpload,
)
from skybluetech_scripts.skybluetech.common.misc.inscribing_template import (
    K_UD_TEMPLATE_GRAPH,
    K_UD_MODIFIED,
    K_UI_TEMPLATE_GRAPH,
    GetTemplateGraph,
)

limiter = PlayerRateLimiter()


def GenerateInscribingTemplateByItemId(template_item_id):
    # type: (str) -> Item
    graph = GetTemplateGraph(template_item_id, CF.CreateGame(LEVEL_ID).GetSeed())
    ud = {
        K_UD_TEMPLATE_GRAPH: [nbt.Int(i) for i in graph],
        "display": {
            "Lore": [
                nbt.String(
                    "§r§d已刻录： " + Item(template_item_id).GetBasicInfo().itemName
                )
            ]
        },
    }
    return Item(INSCRIBING_TEMPLATE, userData=ud)


@ServerItemTryUseEvent.Listen()
def onItemUse(event):
    # type: (ServerItemTryUseEvent) -> None
    if event.item.id != INSCRIBING_TEMPLATE or not limiter.record(event.playerId):
        return
    ud = event.item.userData or {}
    graph_nbt = ud.get(K_UD_TEMPLATE_GRAPH)
    if graph_nbt is None:
        graph = [0] * 25
    else:
        graph = nbt.NBT2Py(graph_nbt)
    PushUIRequest(
        "InscribingTemplateUI.main", params={K_UI_TEMPLATE_GRAPH: graph}
    ).send(event.playerId)


@InscribingTemplateGraphUpload.Listen()
def onGraphUpload(event):
    # type: (InscribingTemplateGraphUpload) -> None
    graph = event.graph
    if not check_list(graph):
        logger.error("Player upload invalid graph: %s" % event.player_id)
        return
    mainhand_item = CF.CreateItem(event.player_id).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mainhand_item = Item.from_dict(mainhand_item) if mainhand_item is not None else None
    if mainhand_item is None or mainhand_item.id != INSCRIBING_TEMPLATE:
        logger.error("Player upload graph failed: %s" % event.player_id)
        return
    ud = mainhand_item.userData or {}
    ud[K_UD_TEMPLATE_GRAPH] = [nbt.Int(i) for i in graph]
    mainhand_item.userData = ud
    if not ud.get(K_UD_MODIFIED, False):
        ud[K_UD_MODIFIED] = True
        ud.setdefault("display", {}).setdefault("Lore", []).append(
            nbt.String("§r§6（被修改）")
        )
    CF.CreateItem(event.player_id).SpawnItemToPlayerCarried(
        mainhand_item.marshal(),
        event.player_id,
    )


def check_list(lst):
    return len(lst) == 25 and all(isinstance(x, int) and 0 <= x <= 7 for x in lst)
