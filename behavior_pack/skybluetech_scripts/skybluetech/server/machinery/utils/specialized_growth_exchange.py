# coding=utf-8


def move_item(source, source_slot, target, target_slots, validate_input=False):
    """转移已成功写入的数量；源槽写入失败时撤回目标写入。"""
    changed = False
    for target_slot in target_slots:
        item = source.GetSlotItem(source_slot)
        if item is None or item.count <= 0:
            break
        if validate_input and not target.IsValidInput(target_slot, item):
            continue
        previous = target.GetSlotItem(target_slot)
        if previous is not None and not previous.CanMerge(item):
            continue
        current_count = previous.count if previous is not None else 0
        count = min(item.count, item.GetBasicInfo().maxStackSize - current_count)
        if count <= 0:
            continue
        added = (previous or item).copy()
        added.count = current_count + count
        remaining = item.copy()
        remaining.count -= count
        if not target.SetSlotItem(target_slot, added):
            continue
        if not source.SetSlotItem(source_slot, remaining if remaining.count > 0 else None):
            if not target.SetSlotItem(target_slot, previous):
                raise RuntimeError("Specialized growth item transfer rollback failed")
            break
        changed = True
    return changed


def move_fluid(source, source_slot, target, target_slot, events, validate_input=False):
    """先维护双方库存，通知统一延至整轮交换完成后发出。"""
    origin = source.fluids[source_slot]
    destination = target.fluids[target_slot]
    fluid_id = origin.fluid_id
    if fluid_id is None or origin.volume <= 0 or not destination.canMerge(fluid_id):
        return False
    if validate_input and not target.IsValidFluidInput(target_slot, fluid_id):
        return False
    amount = min(origin.volume, destination.max_volume - destination.volume)
    if amount <= 0:
        return False
    destination.fluid_id = fluid_id
    destination.volume += amount
    origin.volume -= amount
    events.append((source, False, source_slot, fluid_id, amount))
    events.append((target, True, target_slot, fluid_id, amount))
    return True
