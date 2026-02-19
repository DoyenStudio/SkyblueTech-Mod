# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import (
    AddTextureToOneActor,
    CreateClientEntity,
    DestroyClientEntity,
    SetEntityShadowShow,
    RebuildRenderForOneActor,
)
from ..define.client_molangs import Y_SCALE
from ..define.fluids.gas_enum import IsGas


def GetFluidTexturePath(fluid_id):
    # type: (str) -> str
    return "textures/fluid_models/" + fluid_id.replace(":", ".")


class FluidModel:
    def __init__(self, x, y, z):
        # type: (int, int, int) -> None
        self.fluid_id = ""
        self._last_is_gas = None
        self.x = x
        self.y = y
        self.z = z
        self._try_rebuild()

    def _try_rebuild(self):
        last_is_gas = self._last_is_gas
        now_is_gas = IsGas(self.fluid_id)
        if last_is_gas is None or last_is_gas != now_is_gas:
            if last_is_gas is not None:
                self.Destroy()
            if now_is_gas:
                ceid = CreateClientEntity(
                    "skybluetech:gas_model_entity",
                    (self.x + 0.5, self.y, self.z + 0.5),
                    (0, 0),
                )
            else:
                ceid = CreateClientEntity(
                    "skybluetech:fluid_model_entity",
                    (self.x + 0.5, self.y, self.z + 0.5),
                    (0, 0),
                )
            if ceid is None:
                raise Exception("[ST] Failed to create fluid model")
            self.ceid = ceid
            self._last_is_gas = now_is_gas
            SetEntityShadowShow(self.ceid, False)

    def Destroy(self):
        # type: () -> None
        if self.ceid:
            DestroyClientEntity(self.ceid)
            self.ceid = ""

    def SetTexture(self, fluid_id):
        # type: (str) -> bool
        self.fluid_id = fluid_id
        self._try_rebuild()
        res = AddTextureToOneActor(self.ceid, "default", GetFluidTexturePath(fluid_id))
        if not res:
            print("[ST] Failed to add texture to fluid model")
            return False
        return RebuildRenderForOneActor(self.ceid)

    def SetYScale(self, y_scale):
        # type: (float) -> bool
        return Y_SCALE.set_to_entity(self.ceid, y_scale)
