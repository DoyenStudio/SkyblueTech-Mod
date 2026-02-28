# coding=utf-8

from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.server import (
    DestroyBlockEvent,
    ServerItemUseOnEvent,
    ServerItemTryUseEvent,
    PlayerAttackEntityEvent,
    ServerPlayerTryDestroyBlockEvent,
)
from skybluetech_scripts.tooldelta.api.server import GetPlayerMainhandItem
from .utils import GetUpgraders

# TYPE_CHECKING
if 0:
    from typing import Callable
# TYPE_CHECKING END

upgraders_update_cbs = {}  # type: dict[str, Callable[[Item, dict, dict], None]]
upgrade_reset_cbs = {}  # type: dict[str, Callable[[Item, dict], None]]

destroy_block_cbs = {} # type: dict[str, Callable[[DestroyBlockEvent, Item, dict, dict], None]]
item_use_cbs = {}  # type: dict[str, Callable[[ServerItemTryUseEvent, dict, dict], None]]
item_use_on_block_cbs = {}  # type: dict[str, Callable[[ServerItemUseOnEvent, dict, dict], None]]
block_destroy_cbs = {} # type: dict[str, Callable[[ServerPlayerTryDestroyBlockEvent, Item, dict, dict], None]]
player_attack_cbs = {} # type: dict[str, Callable[[PlayerAttackEntityEvent, Item, dict, dict], None]]


def RegisterDestroyBlockCallback(upgrader_id, callback):
    # type: (str, Callable[[DestroyBlockEvent, Item, dict, dict], None]) -> None
    """
    注册方块被破坏对应的回调。
    """
    destroy_block_cbs[upgrader_id] = callback

def RegisterUpdateCallback(upgrader_id, callback, reset_callback):
    # type: (str, Callable[[Item, dict, dict], None], Callable[[Item, dict]]) -> None
    """
    注册升级对应的回调和重置升级对应的回调。
    """
    upgraders_update_cbs[upgrader_id] = callback
    upgrade_reset_cbs[upgrader_id] = reset_callback

def RegisterItemUseCallback(item_id, callback):
    # type: (str, Callable[[ServerItemTryUseEvent, dict, dict], None]) -> None
    """
    注册物品使用对应的回调。
    """
    item_use_cbs[item_id] = callback

def RegisterItemUseOnCallback(item_id, callback):
    # type: (str, Callable[[ServerItemUseOnEvent, dict, dict]]) -> None
    "注册物品的预使用回调。"
    item_use_on_block_cbs[item_id] = callback

def RegisterBlockDestroyCallback(item_id, callback):
    # type: (str, Callable[[ServerPlayerTryDestroyBlockEvent, Item, dict, dict]]) -> None
    "注册方块破坏对应的回调。"
    block_destroy_cbs[item_id] = callback

def RegisterPlayerAttackCallback(item_id, callback):
    # type: (str, Callable[[PlayerAttackEntityEvent, Item, dict, dict]]) -> None
    "注册玩家攻击对应的回调。"
    player_attack_cbs[item_id] = callback

def UpdateObjectData(obj):
    # type: (Item) -> None
    ud = obj.userData
    if ud is None:
        return
    upgraders = ud.get("st:upgraders", {})
    for upid, upgrade_cb in upgraders_update_cbs.items():
        upgrader_ud = upgraders.get(upid)
        if upgrader_ud is not None:
            upgrade_cb(obj, ud, upgrader_ud)
        else:
            upgrade_reset_cbs[upid](obj, ud)


@ServerItemTryUseEvent.ListenWithUserData(-1000)
def onServerItemTryUse(event):
    # type: (ServerItemTryUseEvent) -> None
    item = event.item
    ud = item.userData
    if ud is None:
        return
    upgraders = GetUpgraders(item)
    for upgrade_id, upgrade_ud in upgraders.items():
        cb = item_use_cbs.get(upgrade_id)
        if cb is not None:
            cb(event, ud, upgrade_ud)


@ServerItemUseOnEvent.ListenWithUserData(-1000)
def onServerItemUseOn(event):
    # type: (ServerItemUseOnEvent) -> None
    item = event.item
    ud = item.userData
    if ud is None:
        return
    upgraders = GetUpgraders(item)
    for upgrade_id, upgrade_ud in upgraders.items():
        cb = item_use_on_block_cbs.get(upgrade_id)
        if cb is not None:
            cb(event, ud, upgrade_ud)

@ServerPlayerTryDestroyBlockEvent.Listen(-1000)
def onServerPlayerTryDestroyBlock(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    item = GetPlayerMainhandItem(event.playerId)
    if item is None:
        return
    ud = item.userData
    if ud is None:
        return
    upgraders = GetUpgraders(item)
    for upgrade_id, upgrade_ud in upgraders.items():
        cb = block_destroy_cbs.get(upgrade_id)
        if cb is not None:
            cb(event, item, ud, upgrade_ud)

@PlayerAttackEntityEvent.Listen(-1000)
def onPlayerAttackEntity(event):
    # type: (PlayerAttackEntityEvent) -> None
    item = GetPlayerMainhandItem(event.playerId)
    if item is None:
        return
    ud = item.userData
    if ud is None:
        return
    upgraders = GetUpgraders(item)
    for upgrade_id, upgrade_ud in upgraders.items():
        cb = player_attack_cbs.get(upgrade_id)
        if cb is not None:
            cb(event, item, ud, upgrade_ud)

@DestroyBlockEvent.Listen(-1000)
def onDestroyBlock(event):
    # type: (DestroyBlockEvent) -> None
    item = GetPlayerMainhandItem(event.playerId)
    if item is None:
        return
    ud = item.userData
    if ud is None:
        return
    upgraders = GetUpgraders(item)
    for upgrade_id, upgrade_ud in upgraders.items():
        cb = destroy_block_cbs.get(upgrade_id)
        if cb is not None:
            cb(event, item, ud, upgrade_ud)
