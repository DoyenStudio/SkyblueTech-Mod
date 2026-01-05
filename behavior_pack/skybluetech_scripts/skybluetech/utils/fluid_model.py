# coding=utf-8

from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.api.client import (
    AddTextureToOneActor,
    CreateClientEntity,
    DestroyClientEntity,
    RegisterQueryMolang,
    SetQueryMolang,
    RebuildRenderForOneActor,
)


@ClientInitCallback()
def onClientSideInit():
    # type: () -> None
    RegisterQueryMolang("query.mod.tank_fluid_y_scale", 0.0)

def GetFluidTexturePath(fluid_id):
    # type: (str) -> str
    return "textures/fluid_models/" + fluid_id.replace(":", ".")
    

class FluidModel:
    def __init__(self, x, y, z , fluid_id, y_scale=None):
        # type: (int, int, int, str, float | None) -> None
        ceid = CreateClientEntity("skybluetech:model_entity", (x+0.5, y, z+0.5), (0, 0))
        if ceid is None:
            raise Exception("[ST] Failed to create fluid model")
        self.ceid = ceid
        self.SetTexture(fluid_id)
        if y_scale is not None:
            self.SetYScale(y_scale)

    def Destroy(self):
        # type: () -> None
        if self.ceid:
            DestroyClientEntity(self.ceid)
            self.ceid = ""

    def SetTexture(self, fluid_id):
        # type: (str) -> None
        res = AddTextureToOneActor(self.ceid, "default", GetFluidTexturePath(fluid_id))
        if not res:
            print("[ST] Failed to add texture to fluid model")
        res = RebuildRenderForOneActor(self.ceid)
        if not res:
            print("[ST] Failed to rebuild render for fluid model")

    def SetYScale(self, y_scale):
        # type: (float) -> None
        SetQueryMolang(self.ceid, "query.mod.tank_fluid_y_scale", y_scale)
