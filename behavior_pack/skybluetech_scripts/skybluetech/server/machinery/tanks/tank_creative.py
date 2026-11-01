# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Tank
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from ..core import RegisterMachine
from .base_tank import BasicTank, RegisterTank


@RegisterMachine
@RegisterTank
class CreativeTank(BasicTank):
    # FluidSlotServer 按液体类型恢复无限供应，存档只写入有限体积标记。
    block_name = Tank.CREATIVE
    fluid_slot_max_volumes = {0: TANK_MAX_VOLUMES[Tank.CREATIVE]}

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        # 空罐销毁管道输入，不设定供液类型；桶和试管仍走手动填充路径。
        if self.CanAddFluid(fluid_id):
            return True, 0
        return False, fluid_volume

    def AddFluidFromFace(self, fluid_id, fluid_volume, relative_face):
        # type: (str, float, str | None) -> tuple[bool, float]
        if 0 not in self.GetFluidInputSlotsForFace(relative_face):
            return False, fluid_volume
        return self.AddFluid(fluid_id, fluid_volume)
