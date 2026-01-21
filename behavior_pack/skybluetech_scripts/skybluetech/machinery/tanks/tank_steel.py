# coding=utf-8
#
from ..basic import RegisterMachine
from .base_tank import BasicTank, RegisterTank


@RegisterMachine
@RegisterTank
class SteelTank(BasicTank):
    block_name = "skybluetech:tank_steel"
    max_fluid_volume = 24000


