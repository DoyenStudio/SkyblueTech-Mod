# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Gas
from .client_molangs import Y_SCALE


def GetFluidTexturePath(fluid_id):
    # type: (str) -> str | None
    texture_info = CF.CreateBlockInfo(LEVEL_ID).GetBlockTextures(fluid_id)
    if not texture_info:
        return None
    # 使用源流体方块的顶面；多贴图变体取首个路径。
    paths = texture_info.get("Up", {}).get("paths", [])
    return paths[0] if paths else None


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
        now_is_gas = self.fluid_id in Gas.all_sub()
        if last_is_gas is None or last_is_gas != now_is_gas:
            if last_is_gas is not None:
                self.Destroy()
            if now_is_gas:
                ceid = GetClient().CreateClientEntityByTypeStr(
                    'skybluetech:gas_model_entity',
                    (self.x + 0.5, self.y, self.z + 0.5),
                    (0, 0),
                )
            else:
                ceid = GetClient().CreateClientEntityByTypeStr(
                    'skybluetech:fluid_model_entity',
                    (self.x + 0.5, self.y, self.z + 0.5),
                    (0, 0),
                )
            if ceid is None:
                raise Exception("[ST] Failed to create fluid model")
            self.ceid = ceid
            self._last_is_gas = now_is_gas
            CF.CreateModel(self.ceid).SetEntityShadowShow(False)

    def Destroy(self):
        # type: () -> None
        if self.ceid:
            GetClient().DestroyClientEntity(self.ceid)
            self.ceid = ""

    def SetTexture(self, fluid_id):
        # type: (str) -> bool
        texture_path = GetFluidTexturePath(fluid_id)
        if not texture_path:
            print("[ST] Failed to get fluid block top texture: " + fluid_id)
            return False
        self.fluid_id = fluid_id
        self._try_rebuild()
        res = CF.CreateActorRender(LEVEL_ID).AddTextureToOneActor(self.ceid, 'default', texture_path)
        if not res:
            print("[ST] Failed to add texture to fluid model")
            return False
        return CF.CreateActorRender(self.ceid).RebuildRenderForOneActor()

    def SetYScale(self, y_scale):
        # type: (float) -> bool
        return Y_SCALE.set_to_entity(self.ceid, y_scale)
