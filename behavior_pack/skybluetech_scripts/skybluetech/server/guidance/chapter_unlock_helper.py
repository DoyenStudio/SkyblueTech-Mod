# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ActorAcquiredItemServerEvent
from ...common.define import chapter_ids

if 0:
    from typing import Callable

callbacks = {}  # type: dict[str, list[Callable[[str, int], str | None]]]


def RegisterCallback(
    item_id,  # type: str
):
    def wrapper(func):
        # type: (Callable[[str, int], str | None]) -> None
        callbacks.setdefault(item_id, []).append(func)

    return wrapper


@ActorAcquiredItemServerEvent.Listen()
def onAcquiredItem(event):
    # type: (ActorAcquiredItemServerEvent) -> None
    for cb in callbacks.get(event.item.id, []):
        cb(event.actor, event.acquireMethod)
