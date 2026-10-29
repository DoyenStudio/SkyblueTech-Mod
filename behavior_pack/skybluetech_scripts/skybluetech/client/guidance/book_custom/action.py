# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.skybluetech.common.define.id_enum import GUIDANCE
from skybluetech_scripts.tooldelta.events.client import ClientItemTryUseEvent

from ...ui.guidance.guidance_ui import GuidanceUI
from ...ui.recipe_checker.minijei_items_page import MiniJEIItemListUI
from .book_main import main_pages


@ClientItemTryUseEvent.Listen()
def onOpenBook(event):
    # type: (ClientItemTryUseEvent) -> None
    if event.item.id != GUIDANCE:
        return
    if not CF.CreatePlayer(GetLocalPlayerId()).isSneaking():
        GuidanceUI.PushUI({"main_pages": main_pages})
    else:
        MiniJEIItemListUI.PushUI({})
    event.cancel()
