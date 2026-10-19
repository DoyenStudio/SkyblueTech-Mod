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
    fluid_slot_max_volumes = (TANK_MAX_VOLUMES[Tank.CREATIVE],)
