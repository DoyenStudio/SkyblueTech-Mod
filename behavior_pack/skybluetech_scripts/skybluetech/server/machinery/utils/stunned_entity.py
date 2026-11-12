# coding=utf-8
from mod.server.extraServerApi import GetEngineActor, GetMinecraftEnum
from skybluetech_scripts.tooldelta.srv import CF
from skybluetech_scripts.tooldelta.events.server import (
    AddEntityServerEvent,
    ActuallyHurtServerEvent,
    ChunkAcquireDiscardedServerEvent,
    DamageEvent,
    EntityDefinitionsEventServerEvent,
    EntityRemoveEvent,
    WillAddEffectServerEvent,
)
from skybluetech_scripts.tooldelta.extensions.entity_utils_server import (
    EntityType,
    GetAiEnabled,
    GetEntityData,
    GetEntityDimension,
    GetEntityPosition,
    GetEntityType,
    IsEntityAlive,
)
from skybluetech_scripts.tooldelta.general import ServerInitCallback, ServerUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ....common.machinery_def.shocker import K_STUNNED

AttrType = GetMinecraftEnum().AttrType

REMOVED_PREFIXES = (
    "minecraft:behavior.",
    "minecraft:navigation.",
    "minecraft:movement.",
    "minecraft:jump.",
)
REMOVED_COMPONENTS = frozenset((
    "minecraft:attack", "minecraft:shooter", "minecraft:teleport",
    "minecraft:flocking", "minecraft:explode", "minecraft:area_attack",
    "minecraft:mob_effect", "minecraft:entity_sensor", "minecraft:target_nearby_sensor",
    "minecraft:environment_sensor", "minecraft:timer", "minecraft:angry",
    "minecraft:transformation",
))
MOVEMENT_ATTRIBUTES = (
    AttrType.SPEED, AttrType.UNDERWATER_SPEED, AttrType.LAVA_SPEED, AttrType.FLYING_SPEED,
)
tracked_entities = set()
pending_restores = {}
failed_restores = set()
effect_guards = {}


def GetEntityComponents(entity_id):
    return CF.CreateEntityEvent(entity_id).GetComponents()


def GetEntityCollisionSize(entity_id):
    return CF.CreateCollisionBox(entity_id).GetSize()


def is_stunned(entity_id):
    if not entity_id or entity_id == "-1":
        return False
    if entity_id in tracked_entities:
        return True
    if IsEntityAlive(entity_id) and GetEntityData(entity_id, K_STUNNED):
        tracked_entities.add(entity_id)
        return True
    return False


def apply_restrictions(entity_id, components):
    success = True
    for name in sorted(components):
        if name.startswith(REMOVED_PREFIXES) or name in REMOVED_COMPONENTS:
            if not CF.CreateEntityEvent(entity_id).RemoveActorComponent(name):
                success = False
    for attr in MOVEMENT_ATTRIBUTES:
        value = CF.CreateAttr(entity_id).GetAttrValue(attr)
        if value is not None and value != 0:
            if not CF.CreateAttr(entity_id).SetAttrValue(attr, 0):
                success = False
    jump_power = CF.CreateGravity(entity_id).GetJumpPower()
    if jump_power is not None and jump_power != 0:
        if not CF.CreateGravity(entity_id).SetJumpPower(0):
            success = False
    CF.CreateAction(entity_id).ResetAttackTarget()
    # Legacy stuns used the engine's AI freeze, which also prevents SetMotion.
    # Keep physics, collision, pushability and buoyancy components untouched.
    ai_enabled = GetAiEnabled(entity_id)
    if ai_enabled is None:
        success = False
    elif not ai_enabled and not CF.CreateControlAi(entity_id).SetBlockControlAi(True, False):
        success = False
    return success


def stun_entity(entity_id):
    if is_stunned(entity_id) or not IsEntityAlive(entity_id):
        return False
    components = GetEntityComponents(entity_id)
    if components is None:
        return False
    if not CF.CreateExtraData(entity_id).SetExtraData(K_STUNNED, True, True):
        return False
    tracked_entities.add(entity_id)
    guard_effect_changes(entity_id)
    if not apply_restrictions(entity_id, components):
        _retry_failed_restore(entity_id)
    else:
        queue_restore(entity_id)
    # A committed permanent intent is accepted even if an engine command
    # needs retrying; reporting failure here would grant a free permanent stun.
    return True


def restore_stun(entity_id):
    if not IsEntityAlive(entity_id) or not GetEntityData(entity_id, K_STUNNED):
        forget_entity(entity_id)
        return
    components = GetEntityComponents(entity_id)
    if components is None:
        _retry_failed_restore(entity_id)
        return
    tracked_entities.add(entity_id)
    guard_effect_changes(entity_id)
    if not apply_restrictions(entity_id, components):
        _retry_failed_restore(entity_id)
    else:
        failed_restores.discard(entity_id)


def _retry_failed_restore(entity_id):
    if entity_id not in failed_restores:
        failed_restores.add(entity_id)
        print("[SkyBlueTech] Retrying stun controls: " + entity_id)
    queue_restore(entity_id, 1.0)


def queue_restore(entity_id, delay=0):
    pending = pending_restores.get(entity_id)
    if pending is not None and (delay > 0 or pending[1] == 0):
        return
    # A definition change must preempt a slower retry after an API failure.
    token = object()
    pending_restores[entity_id] = (token, delay)
    ExecLater(delay, _restore_pending, entity_id, token)


def _restore_pending(entity_id, token):
    pending = pending_restores.get(entity_id)
    if pending is None or pending[0] is not token:
        return
    pending_restores.pop(entity_id, None)
    restore_stun(entity_id)


def forget_entity(entity_id):
    tracked_entities.discard(entity_id)
    pending_restores.pop(entity_id, None)
    failed_restores.discard(entity_id)
    effect_guards.pop(entity_id, None)


def is_player(entity_id):
    if not entity_id or entity_id == "-1":
        return False
    entity_type = GetEntityType(entity_id)
    return (entity_type is not None and (entity_type & EntityType.TypeMask)
            == (EntityType.Player & EntityType.TypeMask))


def guard_effect_changes(entity_id):
    token = object()
    effect_guards[entity_id] = token
    ExecLater(0.2, _clear_effect_guard, entity_id, token)


def _clear_effect_guard(entity_id, token):
    if effect_guards.get(entity_id) is token:
        if entity_id in failed_restores:
            ExecLater(0.2, _clear_effect_guard, entity_id, token)
        else:
            effect_guards.pop(entity_id, None)


@WillAddEffectServerEvent.Listen()
def on_stunned_contact_effect(event):
    if not effect_guards or not is_player(event.entityId):
        return
    for entity_id in tuple(effect_guards):
        if not IsEntityAlive(entity_id):
            continue
        components = GetEntityComponents(entity_id)
        effect = components.get("minecraft:mob_effect") if components else None
        if not effect or effect.get("mob_effect") != event.effectName:
            continue
        effect_range = effect.get("effect_range", 0.2)
        if GetEntityDimension(entity_id) != GetEntityDimension(event.entityId):
            continue
        source_pos = GetEntityPosition(entity_id)
        target_pos = GetEntityPosition(event.entityId)
        source_size = GetEntityCollisionSize(entity_id)
        target_size = GetEntityCollisionSize(event.entityId)
        if (source_pos is None or target_pos is None
                or source_size is None or target_size is None):
            continue
        width = (source_size[0] + target_size[0]) * 0.5 + effect_range
        if (abs(source_pos[0] - target_pos[0]) <= width
                and abs(source_pos[2] - target_pos[2]) <= width
                and source_pos[1] <= target_pos[1] + target_size[1] + effect_range
                and target_pos[1] <= source_pos[1] + source_size[1] + effect_range):
            # This event has no source ID. Limit protection to an active
            # contact-effect component during the brief reconfiguration gap.
            event.cancel()
            return


@DamageEvent.Listen()
def on_stunned_damage(event):
    if is_player(event.entityId) and is_stunned(event.srcId):
        event.DisableDamage()


@ActuallyHurtServerEvent.Listen()
def on_stunned_actual_hurt(event):
    if is_player(event.entityId) and is_stunned(event.srcId):
        event.modifyDamage(0)


@EntityDefinitionsEventServerEvent.Listen()
def on_entity_definition_changed(event):
    if is_stunned(event.entityId):
        guard_effect_changes(event.entityId)
        queue_restore(event.entityId)
        # JSON component-group edits take effect on the following frame.
        ExecLater(0.1, queue_restore, event.entityId)


@AddEntityServerEvent.Listen()
def on_entity_added(event):
    if GetEntityData(event.id, K_STUNNED):
        tracked_entities.add(event.id)
        guard_effect_changes(event.id)
    ExecLater(0, restore_stun, event.id)


@EntityRemoveEvent.Listen()
def on_entity_removed(event):
    forget_entity(event.id)


@ChunkAcquireDiscardedServerEvent.Listen()
def on_chunk_discarded(event):
    for entity_id in event.entities:
        forget_entity(entity_id)


def _restore_loaded_stuns():
    # GetEngineActor returns an entity-id-keyed dictionary.
    for entity_id in GetEngineActor():
        if GetEntityData(entity_id, K_STUNNED):
            tracked_entities.add(entity_id)
            guard_effect_changes(entity_id)
            queue_restore(entity_id)


@ServerInitCallback(priority=-10)
def restore_loaded_stuns():
    ExecLater(0, _restore_loaded_stuns)


@ServerUninitCallback()
def clear_stun_tracking():
    tracked_entities.clear()
    pending_restores.clear()
    failed_restores.clear()
    effect_guards.clear()
