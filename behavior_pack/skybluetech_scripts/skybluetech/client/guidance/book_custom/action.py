# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import ClientItemTryUseEvent
from ....common.define.id_enum import GUIDANCE
from ...ui.guidance.guidance_ui import GuidanceUI
from .book_main import main_pages


@ClientItemTryUseEvent.Listen()
def onOpenBook(event):
    # type: (ClientItemTryUseEvent) -> None
    if event.item.id != GUIDANCE:
        return
    GuidanceUI.PushUI({"main_pages": main_pages})
    event.cancel()
