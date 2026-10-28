# coding=utf-8
from math import sqrt
from random import uniform

from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ....common.define.id_enum import Machinery
from ....common.events.machinery.tesla_plant import TeslaPlantAttack

SPARK_PARTICLE = "skybluetech:tesla_spark"
SHOCK_SOUND = "sfx.skybluetech.tesla_plant.shock"
MAX_SHOCK_SOUNDS = 4
ARC_COLOR = (0.35, 0.75, 1.0)
CORE_COLOR = (0.85, 0.95, 1.0)
ARC_LIFETIME = 0.26
ARC_HALF_WIDTH = 0.6
active_shocks = set()  # type: set[TeslaShock]


class TeslaShock(object):
    """One short discharge; server snapshots also cover lethal hits."""

    def __init__(self, block_pos, end_pos, dim):
        # type: (tuple[int, int, int], tuple[float, float, float], int) -> None
        self.block_pos = block_pos
        self.dim = dim
        x, y, z = block_pos
        self.start_pos = (x + 0.5, y + 2.5, z + 0.5)
        self.end_pos = end_pos
        self.entity_id = None
        self.seed = uniform(0.0, 1000.0)
        self.shapes = []
        self.particle_ids = []
        self.removed = False
        active_shocks.add(self)
        self._create_shader_arc()
        self._redraw()
        particles = CF.CreateParticleSystem(None)
        for pos in (self.start_pos, self.end_pos):
            particle_id = particles.Create(SPARK_PARTICLE, pos, (0, 0, 0))
            if particle_id:
                self.particle_ids.append(particle_id)
        ExecLater(0.07, self._redraw, 0.70)
        ExecLater(0.14, self._redraw, 1.0)
        ExecLater(0.20, self._redraw, 0.25)
        ExecLater(ARC_LIFETIME, self.remove_arc)
        # The spark particles outlive the arc by a fraction of a second.
        ExecLater(0.5, self.remove)

    def _create_shader_arc(self):
        delta = tuple(float(b - a) for a, b in zip(self.start_pos, self.end_pos))
        if sum(value * value for value in delta) < 0.000001:
            return
        # The vertex shader orients the ribbon in view space. WORLD's basis
        # converts this world-space delta without assuming BB axis directions.
        midpoint = tuple((a + b) * 0.5 for a, b in zip(self.start_pos, self.end_pos))
        entity_id = GetClient().CreateClientEntityByTypeStr(
            "skybluetech:tesla_arc", midpoint, (0, 0)
        )
        if not entity_id:
            return
        actor_render = CF.CreateActorRender(entity_id)
        results = (
            actor_render.SetEntityExtraUniforms(1, delta + (ARC_HALF_WIDTH,)),
            actor_render.SetEntityExtraUniforms(2, (self.seed, 1.0, 0.0, 0.0)),
        )
        if not all(results):
            GetClient().DestroyClientEntity(entity_id)
            return
        self.entity_id = entity_id
        CF.CreateModel(entity_id).SetEntityShadowShow(False)

    def _redraw(self, intensity=1.0):
        if self.removed:
            return
        if self.entity_id is not None:
            CF.CreateActorRender(self.entity_id).SetEntityExtraUniforms(
                2, (self.seed, intensity, 0.0, 0.0)
            )
            return
        # Keep a simple discharge if the client cannot create the effect actor
        # or rejects its uniforms. Successful shader arcs allocate no lines.
        self._remove_lines()
        drawing = CF.CreateDrawing(LEVEL_ID)
        sx, sy, sz = self.start_pos
        ex, ey, ez = self.end_pos
        dx, dy, dz = ex - sx, ey - sy, ez - sz
        distance = sqrt(dx * dx + dy * dy + dz * dz)
        steps = max(4, min(24, int(distance * 2)))
        amplitude = min(0.35, distance * 0.08)
        points = [self.start_pos]
        for i in range(1, steps):
            t = float(i) / steps
            # Keep both ends fixed while the interior flickers independently.
            jitter = amplitude * min(1.0, t * 4, (1 - t) * 4)
            points.append((
                sx + dx * t + uniform(-jitter, jitter),
                sy + dy * t + uniform(-jitter, jitter),
                sz + dz * t + uniform(-jitter, jitter),
            ))
        points.append(self.end_pos)
        for i in range(steps):
            color = CORE_COLOR if i % 2 else ARC_COLOR
            line = drawing.AddLineShape(points[i], points[i + 1], color)
            if line is not None:
                self.shapes.append(line)
        # Short side branches make the silhouette read as electricity.
        for i in (steps // 3, steps * 2 // 3):
            px, py, pz = points[i]
            branch_end = (
                px + uniform(-0.45, 0.45),
                py + uniform(-0.45, 0.45),
                pz + uniform(-0.45, 0.45),
            )
            line = drawing.AddLineShape(points[i], branch_end, ARC_COLOR)
            if line is not None:
                self.shapes.append(line)

    def _remove_lines(self):
        for shape in self.shapes:
            shape.Remove()
        self.shapes[:] = []

    def remove_arc(self):
        if self.entity_id is not None:
            GetClient().DestroyClientEntity(self.entity_id)
            self.entity_id = None
        self._remove_lines()

    def remove(self):
        if self.removed:
            return
        self.removed = True
        self.remove_arc()
        particles = CF.CreateParticleSystem(None)
        for particle_id in self.particle_ids:
            particles.Remove(particle_id)
        self.particle_ids[:] = []
        active_shocks.discard(self)


@TeslaPlantAttack.Listen()
def on_tesla_plant_attack(event):
    # type: (TeslaPlantAttack) -> None
    dim = CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension()
    if event.dim != dim:
        return
    block_pos = (event.x, event.y, event.z)
    sound_count = min(len(event.entity_ids), MAX_SHOCK_SOUNDS)
    if sound_count:
        audio = CF.CreateCustomAudio(LEVEL_ID)
        sound_pos = (event.x + 0.5, event.y + 2.5, event.z + 0.5)
        for _ in range(sound_count):
            audio.PlayCustomMusic(SHOCK_SOUND, sound_pos, 1.0, 1.0, False, None)
    for index, entity_id in enumerate(event.entity_ids):
        if index < len(event.target_positions):
            pos = event.target_positions[index]
        else:
            pos = CF.CreatePos(entity_id).GetFootPos()
        if pos is not None and len(pos) == 3:
            TeslaShock(block_pos, tuple(pos), event.dim)


@asModBlockRemovedListener(Machinery.TESLA_PLANT)
def on_tesla_plant_removed(event):
    for shock in tuple(active_shocks):
        x, y, z = shock.block_pos
        if (
            event.dimensionId == shock.dim
            and event.posX == x and event.posZ == z and y <= event.posY <= y + 2
        ):
            shock.remove()


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(_event):
    clear_shocks()


@ClientUninitCallback()
def clear_shocks():
    for shock in tuple(active_shocks):
        shock.remove()
