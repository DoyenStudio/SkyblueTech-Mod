# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Tank
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from ..core import RegisterMachine
from .base_tank import BasicTank, RegisterTank


@RegisterMachine
@RegisterTank
class SteelTank(BasicTank):
    block_name = Tank.STEEL
    max_fluid_volume = TANK_MAX_VOLUMES[Tank.STEEL]
