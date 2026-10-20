# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
    UiInitFinishedEvent,
)
from ...common.define.id_enum import ItemPipe, FluidPipe, Wire
from ...common.events.misc.transmitter_registry import (
    TransmitterRegistryRequest,
    TransmitterRegistrySnapshot,
)

_listened_blocks = set()
_pending_blocks = set()
_ui_ready = False


@UiInitFinishedEvent.Listen()
def on_ui_ready(_):
    global _ui_ready
    _ui_ready = True
    _listen_pending_blocks()
    TransmitterRegistryRequest().send()


def _listen_pending_blocks():
    if _ui_ready and _pending_blocks:
        ClientBlockUseEvent.AddExtraBlocks(set(_pending_blocks))
        _listened_blocks.update(_pending_blocks)
        _pending_blocks.clear()


@TransmitterRegistrySnapshot.Listen()
def on_registry_snapshot(event):
    for kind, enum in (
        ("item_pipe", ItemPipe),
        ("fluid_pipe", FluidPipe),
        ("wire", Wire),
    ):
        block_ids = set(event.kinds.get(kind, ()))
        # all() 返回持久集合，已打开的设置页仍持有同一个对象。
        enum.add_extras(block_ids)
        new_ids = block_ids - _listened_blocks
        if new_ids:
            _pending_blocks.update(new_ids)
    _listen_pending_blocks()
