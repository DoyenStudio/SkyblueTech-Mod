# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.entity_utils_server import (
    CreateEntityRegion,
    DeleteEntityRegion,
    EntityType,
    GetAiEnabled,
    GetEntityData,
    GetEntityDimension,
    GetEntityPosition,
    GetEntityType,
    GetOnlinePlayers,
    IsEntityAlive,
)
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ....common.events.machinery.shocker import ShockerDischarge
from ....common.machinery_def.shocker import K_STUNNED, MAX_TARGET_HEALTH, get_half_energy_cost
from ..core.pool import GetLoadedMachine
from .stunned_entity import GetEntityCollisionSize, stun_entity

AttrType = GetMinecraftEnum().AttrType
ActorDamageCause = GetMinecraftEnum().ActorDamageCause

EFFECT_VIEW_DISTANCE = 128
active_pairs = set()  # type: set[ShockerPair]


def GetEntitiesInRegion(dim, bounds):
    return CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(
        None, tuple(bounds[:3]), tuple(bounds[3:]), dim
    )


def GetHealth(entity_id):
    return CF.CreateAttr(entity_id).GetAttrValue(AttrType.HEALTH)


def HurtWithoutDamage(entity_id):
    return CF.CreateHurt(entity_id).Hurt(
        0, ActorDamageCause.Lightning, None, None, False
    )


def is_mob(entity_id):
    entity_type = GetEntityType(entity_id)
    if entity_type is None or not (entity_type & EntityType.Mob):
        return False
    type_id = entity_type & EntityType.TypeMask
    return type_id not in (
        EntityType.Player & EntityType.TypeMask,
        EntityType.ArmorStand & EntityType.TypeMask,
        EntityType.TripodCamera & EntityType.TypeMask,
        EntityType.Npc & EntityType.TypeMask,
        EntityType.Agent & EntityType.TypeMask,
    )


class ShockerPair(object):
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.dim = first.dim
        self.gap = sum(abs(a - b) for a, b in zip(first.xyz, second.xyz)) - 1
        self.facings = (first.facing, second.facing)
        self.region_name = "skybluetech:shocker:%d:%d:%d:%d:%d:%d:%d" % (
            (self.dim,) + first.xyz + second.xyz
        )
        lower = [min(a, b) for a, b in zip(first.xyz, second.xyz)]
        upper = [value + 1 for value in lower]
        axis = next(i for i, value in enumerate(first.direction) if value)
        lower[axis] += 1
        upper[axis] = max(first.xyz[axis], second.xyz[axis])
        self.bounds = tuple(lower + upper)
        self.members = set()
        self.pending = set()
        self.active = False
        self.region_created = False
        self.flush_scheduled = False

    def start(self):
        self.active = True
        self.first.pair = self.second.pair = self
        active_pairs.add(self)
        self.region_created = CreateEntityRegion(
            self.dim, self.region_name, self.bounds, self._on_region_changed
        )
        if not self.region_created:
            self.close()
        elif self.is_powered():
            self.request_pulse()

    def is_valid(self):
        first, second = self.first, self.second
        return (self.active and first.loaded and second.loaded
                and GetLoadedMachine(self.dim, *first.xyz) is first
                and GetLoadedMachine(self.dim, *second.xyz) is second
                and first.find_partner() is second
                and (first.facing, second.facing) == self.facings)

    def is_powered(self):
        return self.first.redstone_strength > 0 or self.second.redstone_strength > 0

    def _on_region_changed(self, data):
        if not self.active:
            return
        entity_id = data["entityId"]
        if not data["isEnter"]:
            self.members.discard(entity_id)
        elif entity_id not in self.members:
            self.members.add(entity_id)
            if self.is_powered():
                self._queue((entity_id,))

    def _queue(self, entity_ids):
        self.pending.update(entity_ids)
        if self.pending and not self.flush_scheduled:
            self.flush_scheduled = True
            ExecLater(0, self._flush)

    def request_pulse(self):
        # AOI initial callbacks are asynchronous. A pulse takes one snapshot
        # so an immediately following falling edge cannot hide existing mobs.
        entities = GetEntitiesInRegion(self.dim, self.bounds)
        if entities is not None:
            self._queue(entities)

    def _flush(self):
        self.flush_scheduled = False
        pending = self.pending
        self.pending = set()
        if not self.is_valid():
            self.close()
            return
        targets = []
        centre = tuple((a + b) * 0.5 for a, b in zip(self.bounds[:3], self.bounds[3:]))
        # Queueing latches an accepted pulse/entry. A later falling edge or
        # exit must not cancel a discharge that has already been triggered.
        for entity_id in pending:
            if (not IsEntityAlive(entity_id) or not is_mob(entity_id)
                    or GetEntityDimension(entity_id) != self.dim
                    or GetEntityData(entity_id, K_STUNNED)
                    or GetAiEnabled(entity_id) is not True):
                continue
            health = GetHealth(entity_id)
            pos = GetEntityPosition(entity_id)
            if health is None or not 0 < health < MAX_TARGET_HEALTH or pos is None:
                continue
            distance = sum((a - b) ** 2 for a, b in zip(pos, centre))
            targets.append((distance, entity_id, pos))
        targets.sort(key=lambda target: (target[0], target[1]))
        strong = False
        weak_positions = []
        shocked_targets = []
        for _, entity_id, pos in targets:
            # A previous damage callback may remove a target, change its HP,
            # or break the pair, so revalidate before spending either buffer.
            if not self.is_valid():
                break
            if (not IsEntityAlive(entity_id)
                    or GetEntityDimension(entity_id) != self.dim
                    or GetEntityData(entity_id, K_STUNNED)
                    or GetAiEnabled(entity_id) is not True):
                continue
            health = GetHealth(entity_id)
            if health is None or not 0 < health < MAX_TARGET_HEALTH:
                continue
            half_cost = get_half_energy_cost(health, self.gap)
            if self.first.store_rf < half_cost or self.second.store_rf < half_cost:
                HurtWithoutDamage(entity_id)
                weak_positions.append(tuple(float(value) for value in pos))
            elif stun_entity(entity_id):
                self.first.ReducePower(half_cost)
                self.second.ReducePower(half_cost)
                strong = True
                size = GetEntityCollisionSize(entity_id)
                shocked_targets.append((entity_id, GetEntityPosition(entity_id) or pos,
                                        size[1] if size else 1.0))
                HurtWithoutDamage(entity_id)
        if strong or weak_positions:
            ShockerDischarge(
                self.dim, self.first.xyz, self.second.xyz, strong, weak_positions, shocked_targets
            ).sendMulti(self._get_effect_players())

    def _get_effect_players(self):
        # Static geometry does not emit the block-entity appearance events
        # used by BlockSync. Select nearby observers only when discharging.
        players = []
        for player_id in GetOnlinePlayers():
            if GetEntityDimension(player_id) != self.dim:
                continue
            pos = GetEntityPosition(player_id)
            if pos is not None and any(
                sum((a - (b + 0.5)) ** 2 for a, b in zip(pos, machine.xyz))
                <= EFFECT_VIEW_DISTANCE ** 2 for machine in (self.first, self.second)
            ):
                players.append(player_id)
        return players

    def close(self):
        self.active = False
        if self.region_created:
            DeleteEntityRegion(self.dim, self.region_name)
            self.region_created = False
        for machine in (self.first, self.second):
            if machine.pair is self:
                machine.pair = None
        self.members.clear()
        self.pending.clear()
        active_pairs.discard(self)


@ServerUninitCallback()
def clear_pairs():
    for pair in tuple(active_pairs):
        pair.close()
