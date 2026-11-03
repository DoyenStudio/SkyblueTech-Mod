# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.facing import FACING_EN
from skybluetech_scripts.tooldelta.extensions.facing_utils import (
    FacingStrEnum,
    get_relative_facing,
)


class HeatPorts(object):
    """热机与热接口共用的接触面权限；不影响环境换热。

    faces 使用 common.define.facing.RelFacEnum 的相对面成员。
    None 表示全开放，() 表示全关闭，元组表示允许的面。
    例如 heat_output_faces = (RelFacEnum.TOP, RelFacEnum.BACK)。
    """

    heat_input_faces = None  # type: tuple[str, ...] | None
    heat_output_faces = None  # type: tuple[str, ...] | None
    heat_faces_follow_rotation = True
    "无旋转状态的固定模型设为 False，按正面朝北、顶部朝上解释相对面。"

    def _allows_heat_face(self, faces, face):
        # type: (tuple[str, ...] | None, int) -> bool
        if face not in FACING_EN:
            return False
        if faces is None:
            return True
        if not faces:
            return False
        if self.heat_faces_follow_rotation:
            relative_face = self.GetRelativeFacing(FACING_EN[face])
        else:
            relative_face = get_relative_facing(FacingStrEnum.NORTH, FACING_EN[face])
        return relative_face is not None and relative_face in faces

    def CanInputHeat(self, face):
        # type: (int) -> bool
        "检查本方块的世界坐标接触面是否允许受热。"
        return self._allows_heat_face(self.heat_input_faces, face)

    def CanOutputHeat(self, face):
        # type: (int) -> bool
        "检查本方块的世界坐标接触面是否允许供热。"
        return self._allows_heat_face(self.heat_output_faces, face)
