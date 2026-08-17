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
from skybluetech_scripts.tooldelta.api.common import Delay
from skybluetech_scripts.tooldelta.api.server import (
    GetArmorSlotItems,
    GetPlayerMainhandItem,
    SetPlayerAllItems,
    SpawnItemToPlayerCarried,
    SetOneTipMessage,
    SetPlayerUIItem,
)
from ...machinery.utils.charge import (
    ChargeEnough,
    GetCharge,
    GetPowerCost,
    UpdateCharge,
)
from .register import (
    armor_slots,
    item_pre_use_cbs,
    item_pre_use_on_block_cbs,
    tool_items,
    useless_armor_items,
    useless_tool_items,
)
from .utils import MakeItemUseless, MakeToolUseless

# TYPE_CHECKING
if 0>1:
    import typing
# TYPE_CHECKING END

ContainerType = serverApi.GetMinecraftEnum().ContainerType
PlayerUISlot = serverApi.GetMinecraftEnum().PlayerUISlot
ItemPosType = serverApi.GetMinecraftEnum().ItemPosType
SKYBLUE_OBJECTS_TAG = "skybluetech:objects"
RF_PER_DURABILITY = 800
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
def onItemDurabilityChanged(event):
    # type: (ItemDurabilityChangedServerEvent) -> None
    event_item = event.item
    tool_id = useless_tool_items.get(event_item.id, event_item.id)
    if tool_id not in tool_items:
        return
    event.ModifyDurability(event_item.durability or 1)
    onItemDurabilityChangedAfter(event)


@Delay(0)
def onItemDurabilityChangedAfter(event):
    # type: (ItemDurabilityChangedServerEvent) -> None
    event_item = event.item
    tool_id = useless_tool_items.get(event_item.id, event_item.id)
    if tool_id not in tool_items:
        return
    mPlayerId = event.entityId
    mainhand_item = GetPlayerMainhandItem(mPlayerId)
    if mainhand_item is None:
        return
    mainhand_tool_id = useless_tool_items.get(mainhand_item.id, mainhand_item.id)
    if mainhand_tool_id != tool_id:
        return
    ud = mainhand_item.userData
    if ud is None:
        return
    cur_charge, max_charge = GetCharge(ud)
    power_cost = GetPowerCost(ud)
    if cur_charge - power_cost >= 0:
        cur_charge -= power_cost
        useless = False
    else:
        useless = True
    # durability = mainhand_item.durability
    # if durability is not None and event.canChange:
    #     event.ModifyDurability(durability)
    UpdateCharge(mainhand_item, cur_charge)
    if useless:
        MakeToolUseless(mainhand_item)
        SetOneTipMessage(mPlayerId, "工具能量已耗尽")
    SpawnItemToPlayerCarried(mPlayerId, mainhand_item)


@ItemDurabilityChangedServerEvent.ListenWithUserData()
def onArmorDurabilityChanged(event):
    # type: (ItemDurabilityChangedServerEvent) -> None
    item_id = event.item.id
    if item_id in useless_armor_items:
        # _useless 护甲无耐久概念: 取消其耐久变化, 避免被引擎损耗或破坏。
        if event.canChange:
            event.ModifyDurability(event.durabilityBefore)
        return
    if item_id not in armor_slots:
        return
    durability_cost = event.durabilityBefore - event.durability
    if durability_cost <= 0:
        return
    if event.canChange:
        event.ModifyDurability(event.item.durability or event.durabilityBefore or 1)
    onArmorDurabilityChangedAfter(
        event.entityId, item_id, armor_slots[item_id], durability_cost
    )


@Delay(0)
def onArmorDurabilityChangedAfter(player_id, item_id, slot, durability_cost):
    # type: (str, str, int, int) -> None
    slot_item = GetArmorSlotItems(player_id, get_userdata=True).get(slot)
    if slot_item is None or slot_item.id != item_id:
        return
    ud = slot_item.userData
    if ud is None:
        return
    charge, _ = GetCharge(ud)
    cost_rf = (GetPowerCost(ud) or RF_PER_DURABILITY) * durability_cost
    next_charge = max(0, charge - cost_rf)
    UpdateCharge(slot_item, next_charge)
    # 与恢复阈值 ChargeEnough 对称: 余量不足一次消耗(st:cost_rf)即转为 _useless,
    # 与蔚蓝工具"无法支撑下一次使用即耗尽"的判定保持一致(而非耗尽到 0 才触发)。
    if not ChargeEnough(ud):
        MakeItemUseless(slot_item)
        if charge > 0:
            SetOneTipMessage(player_id, "护甲能量已耗尽")
    SetPlayerAllItems(player_id, {(ItemPosType.ARMOR, slot): slot_item})


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
        SetPlayerUIItem(
            event.playerId, event.slot, Item("minecraft:air"), need_back=True
        )
        SetOneTipMessage(event.playerId, "无法将该物品进行附魔/修补/合并等操作")
