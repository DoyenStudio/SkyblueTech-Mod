# coding=utf-8
from math import sqrt

from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent
from skybluetech_scripts.tooldelta.extensions.particle_client import (
    CreateEffectParticle,
    RemoveEffectParticle,
)
from skybluetech_scripts.tooldelta.general import ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ...common.define.id_enum import Machinery
from ...common.events.machinery.shocker import ShockerDischarge, ShockerCoilSpark
from ..utils.electric_arc import ElectricArc
from ..utils.mob_hurt_sounds import MOB_HURT_SOUNDS

WEAK_SPARK_PARTICLE = "skybluetech:shocker_weak_spark"
SHOCK_SOUND = "sfx.skybluetech.shocker.shock"
active_discharges = set()
coil_particles = set()


def GetEffectEntityIdentifier(entity_id):
    return CF.CreateEngineType(entity_id).GetEngineTypeStr()


def GetCurrentDimension():
    return CF.CreateGame(LEVEL_ID).GetCurrentDimension()


def GetBlockName(pos):
    block = CF.CreateBlockInfo(LEVEL_ID).GetBlock(pos)
    return None if block is None else block[0]


def remove_coil_particle(particle_id):
    if particle_id in coil_particles:
        coil_particles.discard(particle_id)
        RemoveEffectParticle(particle_id)


@ShockerCoilSpark.Listen()
def on_coil_spark(event):
    if event.dim != GetCurrentDimension() or GetBlockName(event.pos) != Machinery.SHOCKER:
        return
    for pos in event.points:
        particle_id = CreateEffectParticle(WEAK_SPARK_PARTICLE, tuple(pos))
        if particle_id:
            coil_particles.add(particle_id)
            ExecLater(0.5, remove_coil_particle, particle_id)


def blocks_exist(dim, first_pos, second_pos):
    return (dim == GetCurrentDimension()
            and GetBlockName(first_pos) == Machinery.SHOCKER
            and GetBlockName(second_pos) == Machinery.SHOCKER)


class ShockerEffect(object):
    def __init__(self, event):
        self.dim = event.dim
        self.first_pos = event.first_pos
        self.second_pos = event.second_pos
        self.arc = None
        self.particle_ids = []
        self.removed = False
        delta = tuple(float(b - a) for a, b in zip(self.first_pos, self.second_pos))
        distance = sqrt(sum(value * value for value in delta))
        direction = tuple(value / distance for value in delta)
        start = tuple(a + 0.5 + d * 0.5 for a, d in zip(self.first_pos, direction))
        end = tuple(b + 0.5 - d * 0.5 for b, d in zip(self.second_pos, direction))
        if event.strong:
            self.arc = ElectricArc(start, end)
            sound_pos = tuple((a + b) * 0.5 for a, b in zip(start, end))
            CF.CreateCustomAudio(LEVEL_ID).PlayCustomMusic(
                SHOCK_SOUND, sound_pos, 1.0, 1.0, False, None
            )
        weak_positions = list(event.weak_positions)
        for entity_id, pos, height in event.targets:
            for fraction in (0.2, 0.5, 0.8):
                spark_pos = (pos[0], pos[1] + height * fraction, pos[2])
                particle_id = CreateEffectParticle("skybluetech:shocker_body_spark", spark_pos)
                if particle_id:
                    self.particle_ids.append(particle_id)
            sound = MOB_HURT_SOUNDS.get(GetEffectEntityIdentifier(entity_id))
            if sound:
                name, volume, pitch = sound
                CF.CreateCustomAudio(LEVEL_ID).PlayCustomMusic(
                    name, (pos[0], pos[1] + height * 0.5, pos[2]), volume, pitch, False, None
                )
        if not event.strong:
            weak_positions.extend((start, end))
        for pos in weak_positions:
            particle_id = CreateEffectParticle(WEAK_SPARK_PARTICLE, tuple(pos))
            if particle_id:
                self.particle_ids.append(particle_id)
        active_discharges.add(self)
        ExecLater(0.5, self.remove)
        ExecLater(0.05, self._check_blocks)

    def _check_blocks(self):
        if self.removed:
            return
        if not blocks_exist(self.dim, self.first_pos, self.second_pos):
            self.remove()
            return
        ExecLater(0.05, self._check_blocks)

    def remove(self):
        if self.removed:
            return
        self.removed = True
        if self.arc is not None:
            self.arc.remove()
            self.arc = None
        for particle_id in self.particle_ids:
            RemoveEffectParticle(particle_id)
        self.particle_ids[:] = []
        active_discharges.discard(self)


@ShockerDischarge.Listen()
def on_shocker_discharge(event):
    if (event.first_pos == event.second_pos
            or not blocks_exist(event.dim, event.first_pos, event.second_pos)):
        return
    ShockerEffect(event)


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(_):
    clear_discharges()


@ClientUninitCallback()
def clear_discharges():
    for particle_id in tuple(coil_particles):
        remove_coil_particle(particle_id)
    for discharge in tuple(active_discharges):
        discharge.remove()
