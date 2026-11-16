# coding=utf-8
from math import ceil
from random import uniform

from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent, ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.particle_client import (
    CreateEffectParticle, RemoveEffectParticle,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import ExecLater, Repeat

from ...common.define.facing import FACING_DXYZ
from ...common.define.id_enum import Machinery
from ...common.define.id_enum.fluids import ChemicalGas, CommonGas
from ...common.events.machinery.air_vent import AirVentExhaust
from ...common.machinery_def.air_vent import (
    MODEL_ROTATIONS, FLUID_PER_CYCLE, PARTICLE_LIFETIME,
)

# Particle Create uses ZYX rotations; the emitter's local direction is +Y.
PARTICLE_ROTATIONS = {
    0: (180, 0, 0), 1: (0, 0, 0),
    2: (-90, 0, 0), 3: (90, 0, 0),
    4: (0, 0, 90), 5: (0, 0, -90),
}
PARTICLE_NAME = "skybluetech:air_vent"
loaded_vents = {}
vent_particles = {}


def remove_particle(key, particle_id):
    particles = vent_particles.get(key)
    if particles is not None and particle_id in particles:
        particles.discard(particle_id)
        RemoveEffectParticle(particle_id)
        if not particles:
            vent_particles.pop(key, None)


def remove_vent(key):
    loaded_vents.pop(key, None)
    for particle_id in tuple(vent_particles.get(key, ())):
        remove_particle(key, particle_id)


def update_vent(key, block_info):
    pos = key[1:]
    block_name, aux = block_info.GetBlock(pos) or (None, 0)
    if block_name != Machinery.AIR_VENT:
        remove_vent(key)
        return
    facing = aux & 7
    if facing not in MODEL_ROTATIONS or loaded_vents.get(key) == facing:
        return
    rot_x, rot_y = MODEL_ROTATIONS[facing]
    ok_x = block_info.SetBlockEntityMolangValue(pos, "variable.rotation_x", rot_x)
    ok_y = block_info.SetBlockEntityMolangValue(pos, "variable.rotation_y", rot_y)
    if ok_x and ok_y:
        loaded_vents[key] = facing


@ModBlockEntityLoadedClientEvent.Listen()
def on_vent_loaded(event):
    if event.blockName == Machinery.AIR_VENT:
        key = (event.dimensionId, event.posX, event.posY, event.posZ)
        loaded_vents[key] = None
        update_vent(key, CF.CreateBlockInfo(LEVEL_ID))


@ModBlockEntityRemoveClientEvent.Listen()
def on_vent_removed(event):
    if event.blockName == Machinery.AIR_VENT:
        remove_vent((event.dimensionId, event.posX, event.posY, event.posZ))


@AirVentExhaust.Listen()
def on_exhaust(event):
    if event.dim != CF.CreateGame(LEVEL_ID).GetCurrentDimension():
        return
    if (event.fluid_id not in CommonGas.all_sub()
            and event.fluid_id != ChemicalGas.CARBON_DIOXIDE):
        return
    if event.facing not in MODEL_ROTATIONS or event.volume <= 0:
        return
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    block_name, aux = block_info.GetBlock(event.pos) or (None, 0)
    if block_name != Machinery.AIR_VENT or aux & 7 != event.facing:
        return
    textures = block_info.GetBlockTextures(event.fluid_id) or {}
    texture_key = textures.get("Up", {}).get("name")
    if not texture_key:
        return
    # Query the current atlas layout; resource reloads may repack its regions.
    atlas_uv = block_info.GetTextureAtlasUV(texture_key)
    if not atlas_uv or atlas_uv[2] <= 0 or atlas_uv[3] <= 0:
        return
    particle_system = CF.CreateParticleSystem(None)
    key = (event.dim,) + event.pos
    direction = FACING_DXYZ[event.facing]
    count = max(1, int(ceil(4 * min(event.volume, FLUID_PER_CYCLE) / float(FLUID_PER_CYCLE))))
    for _ in range(count):
        # The opening below the hood is at model Y=8.5, around the outlet axis.
        pos = tuple(event.pos[i] + 0.5 + direction[i] * (0.5 / 16.0)
                    + (uniform(-0.13, 0.13) if direction[i] == 0 else 0)
                    for i in range(3))
        particle_id = CreateEffectParticle(PARTICLE_NAME, pos, PARTICLE_ROTATIONS[event.facing])
        if particle_id:
            if not all(particle_system.SetVariable(particle_id, "variable.gas_" + name, value)
                       for name, value in zip(("u", "v", "w", "h"), atlas_uv)):
                RemoveEffectParticle(particle_id)
                continue
            vent_particles.setdefault(key, set()).add(particle_id)
            ExecLater(PARTICLE_LIFETIME + 0.1, remove_particle, key, particle_id)


@ClientInitCallback()
@Repeat(0.1)
def update_vents():
    if not loaded_vents and not vent_particles:
        return
    dimension = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    for key in set(loaded_vents).union(vent_particles):
        if key[0] == dimension:
            update_vent(key, block_info)
        else:
            remove_vent(key)


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(event):
    for key in set(loaded_vents).union(vent_particles):
        if key[0] == event.fromDimensionId:
            remove_vent(key)


@ClientUninitCallback()
def on_client_uninit():
    for key in set(loaded_vents).union(vent_particles):
        remove_vent(key)
