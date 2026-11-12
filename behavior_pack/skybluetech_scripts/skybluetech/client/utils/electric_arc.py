# coding=utf-8
from math import sqrt
from random import uniform

from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient

from skybluetech_scripts.tooldelta.extensions.particle_client import (
    CreateEffectParticle,
    RemoveEffectParticle,
)
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

SPARK_PARTICLE = "skybluetech:tesla_spark"
ARC_COLOR = (0.35, 0.75, 1.0)
CORE_COLOR = (0.85, 0.95, 1.0)
ARC_LIFETIME = 0.26
ARC_HALF_WIDTH = 0.6


def CreateEffectEntity(identifier, pos, rot=(0, 0)):
    return GetClient().CreateClientEntityByTypeStr(identifier, pos, rot)


def DestroyEffectEntity(entity_id):
    return GetClient().DestroyClientEntity(entity_id)


def SetEffectUniform(entity_id, index, data):
    return CF.CreateActorRender(entity_id).SetEntityExtraUniforms(index, data)


def SetEffectShadow(entity_id, visible):
    return CF.CreateModel(entity_id).SetEntityShadowShow(visible)


def AddEffectLine(start, end, color):
    return CF.CreateDrawing(LEVEL_ID).AddLineShape(start, end, color)


def RemoveEffectLine(shape):
    return shape.Remove()


class ElectricArc(object):
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.entity_id = None
        self.seed = uniform(0.0, 1000.0)
        self.shapes = []
        self.particle_ids = []
        self.removed = False
        self._create_shader_arc()
        self._redraw()
        for pos in (self.start_pos, self.end_pos):
            particle_id = CreateEffectParticle(SPARK_PARTICLE, pos)
            if particle_id:
                self.particle_ids.append(particle_id)
        ExecLater(0.07, self._redraw, 0.70)
        ExecLater(0.14, self._redraw, 1.0)
        ExecLater(0.20, self._redraw, 0.25)
        ExecLater(ARC_LIFETIME, self.remove_arc)
        ExecLater(0.5, self.remove)

    def _create_shader_arc(self):
        delta = tuple(float(b - a) for a, b in zip(self.start_pos, self.end_pos))
        if sum(value * value for value in delta) < 0.000001:
            return
        midpoint = tuple((a + b) * 0.5 for a, b in zip(self.start_pos, self.end_pos))
        entity_id = CreateEffectEntity("skybluetech:tesla_arc", midpoint)
        if not entity_id:
            return
        results = (
            SetEffectUniform(entity_id, 1, delta + (ARC_HALF_WIDTH,)),
            SetEffectUniform(entity_id, 2, (self.seed, 1.0, 0.0, 0.0)),
        )
        if not all(results):
            DestroyEffectEntity(entity_id)
            return
        self.entity_id = entity_id
        SetEffectShadow(entity_id, False)

    def _redraw(self, intensity=1.0):
        if self.removed:
            return
        if self.entity_id is not None:
            SetEffectUniform(self.entity_id, 2, (self.seed, intensity, 0.0, 0.0))
            return
        # Keep the existing line fallback when shader actors cannot be created.
        self._remove_lines()
        sx, sy, sz = self.start_pos
        ex, ey, ez = self.end_pos
        dx, dy, dz = ex - sx, ey - sy, ez - sz
        distance = sqrt(dx * dx + dy * dy + dz * dz)
        steps = max(4, min(24, int(distance * 2)))
        amplitude = min(0.35, distance * 0.08)
        points = [self.start_pos]
        for i in range(1, steps):
            t = float(i) / steps
            jitter = amplitude * min(1.0, t * 4, (1 - t) * 4)
            points.append((
                sx + dx * t + uniform(-jitter, jitter),
                sy + dy * t + uniform(-jitter, jitter),
                sz + dz * t + uniform(-jitter, jitter),
            ))
        points.append(self.end_pos)
        for i in range(steps):
            color = CORE_COLOR if i % 2 else ARC_COLOR
            line = AddEffectLine(points[i], points[i + 1], color)
            if line is not None:
                self.shapes.append(line)
        for i in (steps // 3, steps * 2 // 3):
            px, py, pz = points[i]
            branch_end = (
                px + uniform(-0.45, 0.45),
                py + uniform(-0.45, 0.45),
                pz + uniform(-0.45, 0.45),
            )
            line = AddEffectLine(points[i], branch_end, ARC_COLOR)
            if line is not None:
                self.shapes.append(line)

    def _remove_lines(self):
        for shape in self.shapes:
            RemoveEffectLine(shape)
        self.shapes[:] = []

    def remove_arc(self):
        if self.entity_id is not None:
            DestroyEffectEntity(self.entity_id)
            self.entity_id = None
        self._remove_lines()

    def remove(self):
        if self.removed:
            return
        self.removed = True
        self.remove_arc()
        for particle_id in self.particle_ids:
            RemoveEffectParticle(particle_id)
        self.particle_ids[:] = []
