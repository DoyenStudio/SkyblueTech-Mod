# coding=utf-8

from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)

# TYPE CHECKING
if 0:
    from typing import Callable, TypeVar

    CT = TypeVar("CT", bound=Callable[[ModBlockEntityLoadedClientEvent], None])
    RT = TypeVar("RT", bound=Callable[[ModBlockEntityRemoveClientEvent], None])
# TYPE CHECKING END

mod_block_loaded_cbs = {}  # type: dict[str, list[Callable[[ModBlockEntityLoadedClientEvent], None]]]
mod_block_removed_cbs = {}  # type: dict[str, list[Callable[[ModBlockEntityRemoveClientEvent], None]]]


def asModBlockLoadedListener(
    block_id,  # type: str
):
    def decorator(func):
        # type: (CT) -> CT
        mod_block_loaded_cbs.setdefault(block_id, []).append(func)
        return func

    return decorator


def asModBlockRemovedListener(
    block_id,  # type: str
):
    def decorator(func):
        # type: (RT) -> RT
        mod_block_removed_cbs.setdefault(block_id, []).append(func)
        return func

    return decorator


@ModBlockEntityLoadedClientEvent.Listen()
def _onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    cbs = mod_block_loaded_cbs.get(event.blockName)
    if cbs is None:
        return
    for cb in cbs:
        cb(event)


@ModBlockEntityRemoveClientEvent.Listen()
def _onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    cbs = mod_block_removed_cbs.get(event.blockName)
    if cbs is None:
        return
    for cb in cbs:
        cb(event)
