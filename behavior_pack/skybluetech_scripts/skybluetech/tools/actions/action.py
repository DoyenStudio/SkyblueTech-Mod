# coding=utf-8
#
from mod.server import extraServerApi as serverApi
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import (
    ItemDurabilityChangedServerEvent,
    ServerItemUseOnEvent,
    ServerItemTryUseEvent,
    CraftItemOutputChangeServerEvent,
    UIContainerItemChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.timer import Delay
from skybluetech_scripts.tooldelta.api.server import (
    SetItemTierSpeed,
    GetPlayerMainhandItem,
    SpawnItemToPlayerCarried,
    SetOneTipMessage,
    SetPlayerUIItem,
)
from ...utils.charge import (
    GetCharge,
    GetChargeCost,
    ChargeEnough,
    UpdateCharge,
    SetUpdateChargeCallback,
)
from .register import item_pre_use_cbs, item_pre_use_on_block_cbs, tool_items

# TYPE_CHECKING
if 0:
    from typing import Callable
# TYPE_CHECKING END

ContainerType = serverApi.GetMinecraftEnum().ContainerType
PlayerUISlot = serverApi.GetMinecraftEnum().PlayerUISlot
SKYBLUE_OBJECTS_TAG = "skybluetech:objects"
INVALID_INPUT_SLOTS = {
    PlayerUISlot.EnchantingInput,
    PlayerUISlot.AnvilInput,
    PlayerUISlot.GrindstoneInput,
}
INVALID_TAKEN_CONTAINERS = {
    ContainerType.ANVIL,
    ContainerType.ENCHANTMENT,
    ContainerType.GRINDSTONE,
}
ITEM_INIT_CONTAINERS = {
    ContainerType.INVENTORY,
    ContainerType.CRAFTER,
}


@ServerItemTryUseEvent.ListenWithUserData()
def onServerItemTryUse(event):
    # type: (ServerItemTryUseEvent) -> None
    item = event.item
    if item.id not in item_pre_use_cbs:
        return
    ud = item.userData
    if ud is None:
        return
    item_pre_use_cbs[item.id](event)


@ServerItemUseOnEvent.ListenWithUserData()
def onServerItemUseOn(event):
    # type: (ServerItemUseOnEvent) -> None
    item = event.item
    if item.id not in item_pre_use_on_block_cbs:
        return
    ud = item.userData
    if ud is None:
        return
    item_pre_use_on_block_cbs[item.id](event)


@ItemDurabilityChangedServerEvent.ListenWithUserData()
@Delay(0)
def onItemDurabilityChanged(event):
    # type: (ItemDurabilityChangedServerEvent) -> None
    event_item = event.item
    if event_item.id not in tool_items:
        return
    mPlayerId = event.entityId
    mainhand_item = GetPlayerMainhandItem(mPlayerId)
    if mainhand_item is None or mainhand_item.id != event_item.id:
        return
    ud = mainhand_item.userData
    if ud is None:
        return
    cur_charge, max_charge = GetCharge(ud)
    power_cost = GetChargeCost(ud)
    if cur_charge - power_cost >= 0:
        cur_charge -= power_cost
    else:
        res = SetItemTierSpeed(mainhand_item, 0)
        if not res:
            print("[ERROR] can't set item tier speed for " + mainhand_item.newItemName)
        SetOneTipMessage(mPlayerId, "工具能量已耗尽， 无法继续挖掘方块")
    durability = mainhand_item.durability
    if durability is not None and event.canChange:
        event.ModifyDurability(durability)
    UpdateCharge(mPlayerId, mainhand_item, cur_charge)
    SpawnItemToPlayerCarried(mPlayerId, mainhand_item)


@CraftItemOutputChangeServerEvent.Listen()
def onItemTakeout(event):
    # type: (CraftItemOutputChangeServerEvent) -> None
    if SKYBLUE_OBJECTS_TAG in event.item.GetBasicInfo().tags:
        if event.screenContainerType in INVALID_TAKEN_CONTAINERS:
            event.cancel()
        elif event.screenContainerType in ITEM_INIT_CONTAINERS:
            # item = event.item
            # UpdateCharge(event.playerId, item, 0)
            pass

@UIContainerItemChangedServerEvent.Listen()
@Delay(0)
def onUIItemChanged(event):
    # type: (UIContainerItemChangedServerEvent) -> None
    if event.newItem.id == "minecraft:air":
        return
    if (
        event.slot in INVALID_INPUT_SLOTS
        and SKYBLUE_OBJECTS_TAG in event.newItem.GetBasicInfo().tags
    ):
        SetPlayerUIItem(event.playerId, event.slot, Item("minecraft:air"), need_back=True)
        SetOneTipMessage(event.playerId, "无法将该物品进行附魔/修补/合并等操作")
