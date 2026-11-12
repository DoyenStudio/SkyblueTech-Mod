# coding=utf-8
from collections import Counter
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from ....common.utils import blueprint as bp
from .bans import is_machine_banned

AIR = "minecraft:air"
IGNORE = set("minecraft:" + n for n in (
    "air", "water", "flowing_water", "lava", "flowing_lava", "bedrock", "barrier",
    "structure_void", "structure_block", "jigsaw", "command_block",
    "chain_command_block", "repeating_command_block", "moving_block", "invisible_bedrock",
    "end_portal", "end_gateway", "portal", "fire", "soul_fire", "allow", "deny",
))
CYCLES = {
    "facing_direction": (2, 5, 3, 4),
    "weirdo_direction": (3, 0, 2, 1),
    "direction": (0, 1, 2, 3),
    "coral_direction": (0, 1, 2, 3),
    "torch_facing_direction": bp.DIRECTIONS,
}
RAIL_TURN = (1, 0, 5, 4, 2, 3, 7, 8, 9, 6)


def block_item(name, legacy_aux):
    return CF.CreateItem(LEVEL_ID).GetItemInfoByBlockName(name, legacy_aux, True)


def block_states(name, aux):
    return CF.CreateBlockState(LEVEL_ID).GetBlockStatesFromAuxValue(name, aux)


def legacy_aux(name, states):
    return CF.CreateBlockState(LEVEL_ID).GetBlockAuxValueFromStates(name, states)


def loaded(dim, pos):
    return CF.CreateChunkSource(LEVEL_ID).CheckChunkState(dim, pos)


def bed_color(pos, dim):
    return CF.CreateBlockInfo(LEVEL_ID).GetBedColor(pos, dim)


def rotate_states(states, turns):
    result = {}
    for key, value in states.items():
        short = key.split(":")[-1]
        cycle = CYCLES.get(short, ())
        dest = key
        if value in bp.DIRECTIONS:
            value = bp.DIRECTIONS[(bp.DIRECTIONS.index(value) + turns) % 4]
        elif value in cycle:
            value = cycle[(cycle.index(value) + turns) % 4]
        elif short == "ground_sign_direction":
            value = (value + turns * 4) % 16
        elif short == "rail_direction" and 0 <= value < len(RAIL_TURN):
            for _ in range(turns):
                value = RAIL_TURN[value]
        elif short in ("orientation", "lever_direction") and isinstance(value, (str, bp.py2_unicode)):
            if value.endswith(("_north_south", "_east_west")):
                if turns % 2:
                    axis = "east_west" if value.endswith("north_south") else "north_south"
                    value = value.split("_", 1)[0] + "_" + axis
            else:
                value = "_".join(bp.DIRECTIONS[(bp.DIRECTIONS.index(part) + turns) % 4]
                                 if part in bp.DIRECTIONS else part for part in value.split("_"))
        elif short == "vine_direction_bits":
            value = ((value << turns) | (value >> (4 - turns))) & 15
        elif short == "multi_face_direction_bits":
            horizontal = value >> 2
            horizontal = ((horizontal << turns) | (horizontal >> (4 - turns))) & 15
            value = (horizontal << 2) | (value & 3)
        elif short in ("pillar_axis", "portal_axis") and turns % 2:
            value = {"x": "z", "z": "x"}.get(value, value)
        for direction in bp.DIRECTIONS:
            if direction in short.split("_"):
                dest = key.replace(direction, bp.DIRECTIONS[(bp.DIRECTIONS.index(direction) + turns) % 4])
                break
        result[dest] = value
    return result


class Variant(object):
    def __init__(self, name, aux, turns):
        self.color = None
        if name == "minecraft:bed":
            self.color = (aux >> 8) - 1 if aux >> 8 else 1
            if not 0 <= self.color <= 15:
                raise ValueError(name)
            aux &= 255
        states = block_states(name, aux)
        info = CF.CreateBlockInfo(LEVEL_ID).GetBlockBasicInfo(name) or {}
        if (name in IGNORE or states is None or info.get("destroyTime", -1) < 0
                or "liquid_depth" in states or is_machine_banned(name)
                or legacy_aux(name, states) != aux):
            raise ValueError(name)
        item = block_item(name, aux) or {}
        if not item.get("newItemName") or item["newItemName"] == AIR:
            raise ValueError(name)
        self.name = name
        self.solid = bool(info.get("solid"))
        self.item = bp.material_key(item["newItemName"], item.get("newAuxValue", 0))
        if self.color is not None:
            self.item = (self.item[0], 15 - self.color)
        self.count = 2 if "double" in name.split(":")[1].split("_") and "slab" in name else 1
        self.states = rotate_states(states, turns)
        self.aux = legacy_aux(name, self.states)
        if self.aux < 0:
            raise ValueError(name)
        self.partner = None
        self.secondary = False
        if "upper_block_bit" in self.states:
            self.secondary = self.states["upper_block_bit"]
            self.partner = (0, -1 if self.secondary else 1, 0)
        elif "head_piece_bit" in self.states:
            self.secondary = self.states["head_piece_bit"]
            direction = self.states.get("direction", 0)
            offset = bp.FORWARD[(direction + 2) % 4]
            self.partner = tuple(-v for v in offset) if self.secondary else offset


class Layout(object):
    def __init__(self, snapshot, pos, facing, skipped=None):
        size, anchor, source, groups = snapshot
        self.turns = (facing - source) % 4
        origin = bp.front(pos, facing)
        cells = {}
        self.variants = []
        for (name, aux), indices in sorted(groups.items()):
            variant = Variant(name, aux, self.turns)
            self.variants.append((variant.name, variant.aux, variant.states, variant.color))
            for index in indices:
                target = bp.world(bp.local(index, size), anchor, origin, self.turns)
                cells[target] = variant
        self.units = []
        self.counts = Counter()
        # Build walls and supports before decorations attached to their sides.
        for at in sorted(cells, key=lambda p: (not cells[p].solid, p[1], p[0], p[2])):
            variant = cells[at]
            parts = [(at, variant)]
            if variant.partner:
                other = tuple(a + b for a, b in zip(at, variant.partner))
                mate = cells.get(other)
                if (not mate or mate.name != variant.name or mate.color != variant.color or mate.secondary == variant.secondary
                        or mate.partner != tuple(-v for v in variant.partner)):
                    if skipped is None:
                        raise ValueError("蓝图包含不完整的方块：" + variant.name)
                    skipped.append(at)
                    continue
                if variant.secondary:
                    continue
                parts.append((other, mate))
            self.units.append((parts, variant.item, variant.count))
            self.counts[variant.item] += variant.count


def inspect_unit(dim, parts):
    """Return missing cells, or the first conflict. None means unloaded."""
    missing = []
    info, state = CF.CreateBlockInfo(LEVEL_ID), CF.CreateBlockState(LEVEL_ID)
    for pos, variant in parts:
        if not loaded(dim, pos):
            return None, None
        block = info.GetBlockNew(pos, dim)
        if not block:
            return None, None
        if block["name"] == AIR:
            missing.append((pos, variant))
        elif block["name"] != variant.name or state.GetBlockStates(pos, dim) != variant.states:
            return [], pos
        elif variant.color is not None and bed_color(pos, dim) != variant.color:
            return [], pos
    return missing, None
