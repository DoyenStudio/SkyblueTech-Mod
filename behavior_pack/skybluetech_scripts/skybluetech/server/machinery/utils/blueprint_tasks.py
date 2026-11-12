# coding=utf-8
from collections import Counter
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from ....common.utils import blueprint as bp
from .blueprint_layout import AIR, Variant, Layout, inspect_unit, loaded, legacy_aux, bed_color
from .blueprint_inventory import reserve, consume, refund

CHECK_BATCH = 192
BUILD_BATCH = 24


def set_bed_color(pos, color, dim):
    return CF.CreateBlockInfo(LEVEL_ID).SetBedColor(pos, color, dim)


def capture(machine, player, target):
    facing = machine.facing()
    origin = bp.front(machine.xyz, facing)
    low, size = bp.bounds(origin, target)
    anchor = tuple(a - b for a, b in zip(origin, low))
    groups, skipped, variants = {}, Counter(), {}
    info = CF.CreateBlockInfo(LEVEL_ID)
    state_comp = CF.CreateBlockState(LEVEL_ID)
    chunks = set()
    volume = size[0] * size[1] * size[2]
    for index in bp.py2_xrange(volume):
        if index and index % 256 == 0:
            chunks.clear()
            yield
        pos = tuple(a + b for a, b in zip(low, bp.local(index, size)))
        chunk = pos[0] // 16, pos[2] // 16
        if chunk not in chunks:
            if not loaded(machine.dim, pos):
                raise ValueError("选区含未加载区块")
            chunks.add(chunk)
        block = info.GetBlockNew(pos, machine.dim)
        if not block:
            raise ValueError("无法读取选区")
        name = block["name"]
        if name == AIR:
            continue
        # Region palettes trim air margins and omit the secondary halves of
        # doors/beds. Read the actual cells so offsets and both halves survive.
        states = state_comp.GetBlockStates(pos, machine.dim)
        if states is None:
            raise ValueError("无法读取方块状态")
        aux = legacy_aux(name, states)
        if name == "minecraft:bed" and aux >= 0:
            color = bed_color(pos, machine.dim)
            if color >= 0:
                aux |= (color + 1) << 8
        key = name, aux
        if key not in variants:
            try:
                variants[key] = Variant(name, aux, 0)
            except ValueError:
                variants[key] = None
        if variants[key] is None:
            skipped[name] += 1
        else:
            groups.setdefault(key, []).append(index)
    if not groups:
        detail = "、".join("%s ×%d" % pair for pair in sorted(skipped.items()))
        raise ValueError("没有可保存的方块" + ("，已忽略：" + detail if detail else ""))
    snapshot = size, anchor, facing, groups
    incomplete = []
    layout = Layout(snapshot, machine.xyz, facing, incomplete)
    if incomplete:
        bad = set(bp.linear(tuple(a - b for a, b in zip(at, low)), size) for at in incomplete)
        for key, indices in list(groups.items()):
            kept = [index for index in indices if index not in bad]
            if len(kept) != len(indices):
                skipped[key[0]] += len(indices) - len(kept)
            if kept:
                groups[key] = kept
            else:
                del groups[key]
    if not groups:
        raise ValueError("没有可保存的完整方块")
    blob = bp.pack(*snapshot)
    machine.save_snapshot(blob)
    machine.bdata["bp_output"] = ""
    machine.saved_counts = layout.counts
    machine.status = "已保存选区"
    if skipped:
        machine.status += "，已忽略：" + "、".join("%s ×%d" % pair for pair in sorted(skipped.items()))
    machine.notice(player, machine.status)
    machine.reopen(player)


def examine(machine, player, start):
    code = machine.draft()
    layout = machine.layout
    needed, planned = Counter(), bytearray((len(layout.units) + 7) // 8)
    conflict = None
    for index, (parts, item, count) in enumerate(layout.units):
        missing, blocked = inspect_unit(machine.dim, parts)
        if missing is None and blocked is None:
            raise ValueError("蓝图区域含未加载区块")
        if blocked:
            conflict = conflict or blocked
        if missing or blocked:
            needed[item] += count
            planned[index // 8] |= 1 << (index % 8)
        if (index + 1) % CHECK_BATCH == 0:
            yield
    machine.needs = needed
    machine.status = "方块冲突 %s" % (conflict,) if conflict else ""
    if not needed:
        machine.status = "蓝图已全部搭建"
    if start and not conflict:
        if not machine.ui_sync.PlayerInSync(player):
            return
        if not needed:
            machine.status = "蓝图已全部搭建"
        else:
            escrow = []
            if reserve(player, needed, escrow):
                machine.start_job(player, code, planned, escrow)
            else:
                machine.status = "背包材料不足或槽位已变化"
                machine.return_stacks(player, escrow)


def place_unit(dim, info, parts, missing):
    at, first = missing[0]
    if len(parts) == 1:
        placed = info.SetBlockNew(at, {"name": first.name, "aux": first.aux}, 2, dim, True)
        return placed, placed

    # SetBlockNew builds both bed halves around its head, and both door
    # halves around the bottom. Preflight checked the complete footprint.
    if first.color is not None:
        at, first = parts[1]
    old = info.GetBlockNew(at, dim)
    handling = 0 if old and old["name"] == first.name else 2
    placed = info.SetBlockNew(at, {"name": first.name, "aux": first.aux}, handling, dim, True)
    state = CF.CreateBlockState(LEVEL_ID)
    for pos, variant in parts:
        block = info.GetBlockNew(pos, dim) or {}
        if block.get("name") != variant.name:
            break
        if state.GetBlockStates(pos, dim) != variant.states:
            if not state.SetBlockStates(pos, variant.states, dim):
                break
    else:
        if first.color is not None and bed_color(at, dim) != first.color:
            set_bed_color(at, first.color, dim)
        remaining, conflict = inspect_unit(dim, parts)
        if remaining == [] and conflict is None:
            return True, True
    # Restore newly occupied cells if the engine rejected a companion half.
    for pos, variant in missing:
        if (info.GetBlockNew(pos, dim) or {}).get("name") == variant.name:
            if not info.SetBlockNew(pos, {"name": AIR, "aux": 0}, 0, dim, True, False):
                return False, placed
    return False, False


def build_batch(machine):
    job = machine.job
    if job["returning"]:
        machine.finish_job()
        return
    layout = machine.layout
    info = CF.CreateBlockInfo(LEVEL_ID)
    previous_index = job["index"]
    for _ in range(BUILD_BATCH):
        index = job["index"]
        if index >= len(layout.units):
            machine.stop_job("搭建完成")
            return
        parts, item, count = layout.units[index]
        missing, blocked = inspect_unit(machine.dim, parts)
        if missing is None and blocked is None:
            break
        paid = machine.planned[index // 8] & (1 << (index % 8))
        if blocked or (missing and not paid):
            machine.stop_job("搭建中止，目标已变化 %s" % (blocked or missing[0][0],))
            return
        if missing:
            success, spent = place_unit(machine.dim, info, parts, missing)
            if spent:
                consume(job["escrow"], item, count)
            if not success:
                machine.stop_job("无法放置方块 %s" % (missing[0][0],))
                return
        job["index"] += 1
    if job["index"] != previous_index:
        machine.checkpoint()
