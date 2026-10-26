# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Gas
from skybluetech_scripts.skybluetech.client.utils.client_molangs import (
    FLUID_VOLUME_DEPTH,
    FLUID_VOLUME_HEIGHT,
    FLUID_VOLUME_MODE,
    FLUID_VOLUME_TEXTURE,
    FLUID_VOLUME_WIDTH,
    Y_SCALE,
)
from skybluetech_scripts.skybluetech.client.utils.fluid_texture_frames import (
    FLUID_TEXTURE_FRAMES,
    FLUID_VOLUME_TEXTURE_INDICES,
)


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


class FluidVolumeModel(object):
    "复用流体模型实体的体积模式，位置为液柱底面中心，尺寸单位为方块。"

    def __init__(self, center_x, base_y, center_z):
        # type: (float, float, float) -> None
        self.pos = (center_x, base_y, center_z)
        self.ceid = ""
        self.fluid_id = ""

    def _ensure_entity(self):
        # type: () -> bool
        if self.ceid:
            return True
        entity_id = GetClient().CreateClientEntityByTypeStr(
            "skybluetech:fluid_model_entity", self.pos, (0, 0)
        )
        if not entity_id:
            return False
        self.ceid = entity_id
        CF.CreateModel(entity_id).SetEntityShadowShow(False)
        if not FLUID_VOLUME_MODE.set_to_entity(entity_id, 1.0):
            self.Destroy()
            return False
        return True

    def SetTexture(self, fluid_id):
        # type: (str) -> bool
        texture_path = GetFluidTexturePath(fluid_id)
        if not texture_path or not self._ensure_entity():
            return False
        texture_key = texture_path.replace("\\", "/")
        if texture_key.endswith(".png"):
            texture_key = texture_key[:-4]
        # 未识别贴图由 GLES3 查询尺寸；GLES2 保留静态回退，不猜动画帧数。
        frame_count, frame_rate = FLUID_TEXTURE_FRAMES.get(texture_key, (0, 0.0))
        actor_render = CF.CreateActorRender(self.ceid)
        texture_index = FLUID_VOLUME_TEXTURE_INDICES.get(texture_key, 0)
        # 蒸发池贴图预先声明，由渲染控制器选择。首次动态替换贴图在重进后
        # 可能只更新可查询路径、实际仍采样初始占位图，不能靠返回值判定成功。
        if texture_index == 0:
            if not CF.CreateActorRender(LEVEL_ID).AddTextureToOneActor(
                self.ceid, "volume", texture_path
            ):
                return False
            if not actor_render.RebuildRenderForOneActor():
                return False
        if not actor_render.SetEntityExtraUniforms(
            1, (float(frame_count), float(frame_rate), 0.0, 0.0)
        ):
            return False
        if not FLUID_VOLUME_TEXTURE.set_to_entity(self.ceid, float(texture_index)):
            return False
        self.fluid_id = fluid_id
        return True

    def SetSize(self, width, height, depth):
        # type: (float, float, float) -> bool
        size = (float(width), float(height), float(depth))
        if not all(0.0 < value < float("inf") for value in size):
            return False
        if not self._ensure_entity():
            return False
        # 不短路：部分失败时仍写入其余轴，调用方下次整体重试。
        results = (
            FLUID_VOLUME_WIDTH.set_to_entity(self.ceid, size[0]),
            FLUID_VOLUME_HEIGHT.set_to_entity(self.ceid, size[1]),
            FLUID_VOLUME_DEPTH.set_to_entity(self.ceid, size[2]),
        )
        return all(results)

    def SetYScale(self, fill_ratio):
        # type: (float) -> bool
        fill_ratio = float(fill_ratio)
        if fill_ratio != fill_ratio or not self._ensure_entity():
            return False
        return Y_SCALE.set_to_entity(self.ceid, max(0.0, min(1.0, fill_ratio)))

    def Destroy(self):
        # type: () -> None
        if self.ceid:
            GetClient().DestroyClientEntity(self.ceid)
            self.ceid = ""
        self.fluid_id = ""
