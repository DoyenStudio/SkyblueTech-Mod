# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.particle_client import (
    CreateEffectParticle, RemoveEffectParticle,
)

from ...common.define.id_enum import Machinery
from ...common.events.machinery.effluent_outfall import EffluentOutfallDischarge


@EffluentOutfallDischarge.Listen()
def on_discharge(event):
    if CF.CreateGame(LEVEL_ID).GetCurrentDimension() != event.dim:
        return
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    block = block_info.GetBlock(event.pos)
    if not block or block[0] != Machinery.EFFLUENT_OUTFALL:
        return
    textures = block_info.GetBlockTextures(event.fluid_id) or {}
    texture_key = (textures.get("Up") or {}).get("name")
    region = block_info.GetTextureAtlasUV(texture_key) if texture_key else None
    if not region or region[2] <= 0 or region[3] <= 0:
        return

    center = tuple(coord + 0.5 for coord in event.pos)
    emitter = CreateEffectParticle("skybluetech:effluent_outfall", center)
    if not emitter:
        return
    system = CF.CreateParticleSystem(None)
    for name, value in zip(("u", "v", "w", "h"), region):
        if not system.SetVariable(emitter, "variable.fluid_" + name, value):
            RemoveEffectParticle(emitter)
            return
    system.EmitManually(emitter)
    system.EmitManually(emitter)
