# coding=utf-8
from collections import Counter
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetServer
from mod.server.extraServerApi import GetMinecraftEnum, GetPlayerList
from skybluetech_scripts.tooldelta.events.server.world import AddServerPlayerEvent
from ....common.utils.blueprint import material_key

INVENTORY = GetMinecraftEnum().ItemPosType.INVENTORY
REFUND_KEY = "skybluetech:blueprint_refunds"


def inventory(player):
    return CF.CreateItem(player).GetPlayerAllItems(INVENTORY, True) or []


def key(stack):
    return material_key(stack["newItemName"], stack.get("newAuxValue", 0))


def available(stacks):
    counts = Counter()
    for stack in stacks:
        if stack and stack.get("count", 0) > 0:
            counts[key(stack)] += stack["count"]
    return counts


def reserve(player, needs, escrow):
    stacks = inventory(player)
    if needs - available(stacks):
        return False
    remaining = needs.copy()
    comp = CF.CreateItem(player)
    for slot, stack in enumerate(stacks):
        if not stack:
            continue
        material = key(stack)
        take = min(remaining[material], stack["count"])
        if take:
            if comp.GetPlayerItem(INVENTORY, slot, True) != stack:
                return False
            if not comp.SetInvItemNum(slot, stack["count"] - take):
                return False
            escrow.append(dict(stack, count=take))
            remaining[material] -= take
    return True


def consume(escrow, material, count):
    for stack in list(escrow):
        if key(stack) == material:
            take = min(stack["count"], count)
            stack["count"] -= take
            count -= take
            if not stack["count"]:
                escrow.remove(stack)
            if not count:
                return
    raise ValueError("missing reserved material")


def refund(escrow, player, dim, pos):
    drop = (pos[0] + 0.5, pos[1] + 1, pos[2] + 0.5)
    for stack in list(escrow):
        if player in GetPlayerList():
            material = key(stack)
            before = available(inventory(player))[material]
            if CF.CreateItem(player).SpawnItemToPlayerInv(stack, player):
                escrow.remove(stack)
                continue
            # A full bag can accept a partial stack while returning False.
            added = max(0, available(inventory(player))[material] - before)
            stack["count"] -= min(added, stack["count"])
        if not stack["count"] or GetServer().CreateEngineItemEntity(stack, dim, drop):
            escrow.remove(stack)


def finish_destroyed_refund(escrow, player, dim, pos):
    refund(escrow, player, dim, pos)
    if escrow:
        data = CF.CreateExtraData(LEVEL_ID)
        pending = data.GetExtraData(REFUND_KEY) or {}
        pending.setdefault(player, []).extend(escrow)
        data.SetExtraData(REFUND_KEY, pending, True)


@AddServerPlayerEvent.Listen()
def deliver_remaining(event):
    data = CF.CreateExtraData(LEVEL_ID)
    pending = data.GetExtraData(REFUND_KEY) or {}
    stacks = pending.get(event.id)
    if stacks:
        pos = CF.CreatePos(event.id).GetFootPos()
        if pos:
            refund(stacks, event.id, CF.CreateDimension(event.id).GetEntityDimensionId(), pos)
            if not stacks:
                pending.pop(event.id)
            data.SetExtraData(REFUND_KEY, pending, True)
