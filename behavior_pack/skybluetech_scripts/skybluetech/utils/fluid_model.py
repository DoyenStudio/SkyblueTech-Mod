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
    def __init__(self, x, y, z):
        # type: (int, int, int) -> None
        ceid = CreateClientEntity("skybluetech:model_entity", (x+0.5, y, z+0.5), (0, 0))
        if ceid is None:
            raise Exception("[ST] Failed to create fluid model")
        self.ceid = ceid

    def Destroy(self):
        # type: () -> None
        if self.ceid:
            DestroyClientEntity(self.ceid)
            self.ceid = ""

    def SetTexture(self, fluid_id):
        # type: (str) -> bool
        res = AddTextureToOneActor(self.ceid, "default", GetFluidTexturePath(fluid_id))
        if not res:
            print("[ST] Failed to add texture to fluid model")
            return False
        return RebuildRenderForOneActor(self.ceid)

    def SetYScale(self, y_scale):
        # type: (float) -> bool
        return SetQueryMolang(self.ceid, "query.mod.tank_fluid_y_scale", y_scale)
