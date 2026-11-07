# coding=utf-8
"""Pair-wise optional transactions; native inventories remain host-owned."""
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault

from ... import transferlib
from .nbt_utils import _get_container_nbt


def _clear_inventory_cache(network):
    from .logic import logic_module
    # A provider may persist through NBT without a container-change event.
    # Other networks can share its inventory or be changed by its callbacks.
    for current in set(logic_module.networks_pool) | set((network,)):
        current._cache_datas.clear()
        current._cache_block_names.clear()
        current._cache_slotposes.clear()
        current._cache_slotitems.clear()


def _unique_chests(network, access_points):
    from .logic import _is_chest
    seen = set()
    result = []
    for ap in access_points:
        pos = ap.target_pos
        if _is_chest(network, pos):
            data, _ = _get_container_nbt(network.dim, pos, network._cache_datas)
            x = GetValueWithDefault(data or {}, "pairx", None)
            z = GetValueWithDefault(data or {}, "pairz", None)
            if x is not None and z is not None:
                pair = (x, pos[1], z)
                key = (min(pos, pair), max(pos, pair))
                if key in seen:
                    continue
                seen.add(key)
        result.append(ap)
    return result


def _move(api, source, target, budget):
    moved = 0
    with api.open_transaction() as tx:
        # Bulk extraction preserves custom endpoint rules. Repeated identities
        # need only one attempt, even when they occupy several sparse slots.
        resources = set()
        for slot in source.get_slots():
            resource = source.get_resource(slot, tx)
            if resource is None or resource in resources:
                continue
            resources.add(resource)
            moved += api.move_item(source, target, resource, budget - moved, tx)
            if moved == budget:
                break
        tx.commit()
    return moved


def tick(network):
    from .logic import _legacy_network_tick
    api = transferlib.api
    budget = network.transfer_speed
    inputs = network.get_input_access_points()
    outputs = network.get_output_access_points()
    if budget <= 0 or not inputs or not outputs:
        return

    start = network._output_cursor % len(outputs)
    network._output_cursor = (start + 1) % len(outputs)
    outputs = _unique_chests(network, outputs[start:] + outputs[:start])
    inputs = _unique_chests(network, inputs)
    native_items = CF.CreateItem(LEVEL_ID)
    for output_ap in outputs:
        for input_ap in inputs:
            if output_ap.target_pos == input_ap.target_pos:
                continue
            try:
                # Query both sides before choosing the backend. Exceptions are
                # not evidence of an unsupported port and never cause fallback.
                source = transferlib.at_access(api.ITEM, output_ap)
                target = transferlib.at_access(api.ITEM, input_ap)
                if source is not None and target is not None:
                    try:
                        moved = _move(api, source, target, budget)
                    finally:
                        _clear_inventory_cache(network)
                else:
                    source_size = native_items.GetContainerSize(output_ap.target_pos, network.dim)
                    target_size = native_items.GetContainerSize(input_ap.target_pos, network.dim)
                    if not source_size or source_size <= 0 or not target_size or target_size <= 0:
                        continue
                    # This call writes all its pending native changes before
                    # returning; no old snapshot survives across a transaction.
                    moved = _legacy_network_tick(
                        network, (input_ap,), (output_ap,), budget)
                budget -= moved
            except api.TransactionError:
                _clear_inventory_cache(network)
                continue
            if budget <= 0:
                return
