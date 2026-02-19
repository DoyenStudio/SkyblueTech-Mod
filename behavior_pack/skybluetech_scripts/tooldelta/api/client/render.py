# coding=utf-8

from ...internal import ClientComp, GetClient, ClientLevelId
from ..internal.cacher import MethodCacher, AttrCacher

_copyActorTextureFromPlayer = MethodCacher(
    lambda: ClientComp.CreateActorRender(ClientLevelId).CopyActorTextureFromPlayer
)
_setRenderLocalPlayer = MethodCacher(
    lambda: ClientComp.CreateActorRender(ClientLevelId).SetNotRenderAtAll
)


def CopyActorTextureFromPlayer(
    from_player_id, actor_identifier, from_key="default", new_key="default"
):
    # type: (str, str, str, str) -> bool
    return _copyActorTextureFromPlayer(
        from_player_id, actor_identifier, from_key, new_key
    )


def SetRenderLocalPlayer(enable):
    # type: (bool) -> bool
    return _setRenderLocalPlayer(enable)


def SetNotRenderAtAll(entity_id, not_render):
    # type: (str, bool) -> bool
    return ClientComp.CreateActorRender(entity_id).SetNotRenderAtAll(not_render)


def PlayParticleAt(particle_path, pos):
    # type: (str, tuple[float, float, float]) -> bool
    par_id = GetClient().CreateEngineParticle(particle_path, pos)
    if par_id is None:
        raise ValueError("Particle path not found: " + particle_path)
    return ClientComp.CreateParticleControl(par_id).Play()


def PlayParticleOn(particle_name, entity_id):
    # type: (str, str) -> bool
    comp = ClientComp.CreateParticleSystem(None)
    par_id = comp.Create(particle_name)
    return comp.BindEntity(par_id, entity_id)


def AddActorBlockGeometry(entity_id, geo_id, offset=(0, 0, 0), rotation=(0, 0, 0)):
    # type: (str, str, tuple[float, float, float], tuple[float, float, float]) -> bool
    return ClientComp.CreateActorRender(entity_id).AddActorBlockGeometry(
        geo_id, offset, rotation
    )


def DeleteActorBlockGeometry(entity_id, geo_id):
    # type: (str, str) -> bool
    return ClientComp.CreateActorRender(entity_id).DeleteActorBlockGeometry(geo_id)


def SetActorBlockGeometryScale(entity_id, geo_id, scale):
    # type: (str, str, tuple[float, float, float]) -> bool
    return ClientComp.CreateActorRender(entity_id).SetActorBlockGeometryScale(
        geo_id, scale
    )


def RebuildRenderForOneActor(entity_id):
    # type: (str) -> bool
    return ClientComp.CreateActorRender(entity_id).RebuildRenderForOneActor()


def SetEntityOpacity(entity_id, opacity):
    # type: (str, float) -> None
    ClientComp.CreateModel(entity_id).SetEntityOpacity(opacity)


def SetEntityShadowShow(entity_id, show):
    # type: (str, bool) -> None
    ClientComp.CreateModel(entity_id).SetEntityShadowShow(show)


AddTextureToOneActor = MethodCacher(
    lambda: ClientComp.CreateActorRender(ClientLevelId).AddTextureToOneActor
)
CreateShapeFactory = AttrCacher(lambda: ClientComp.CreateDrawing(ClientLevelId))


__all__ = [
    "CopyActorTextureFromPlayer",
    "CreateShapeFactory",
    "SetRenderLocalPlayer",
    "SetNotRenderAtAll",
    "SetActorBlockGeometryScale",
    "SetEntityOpacity",
    "SetEntityShadowShow",
    "AddActorBlockGeometry",
    "DeleteActorBlockGeometry",
    "RebuildRenderForOneActor",
    "AddTextureToOneActor",
    "PlayParticleAt",
    "PlayParticleOn",
]
