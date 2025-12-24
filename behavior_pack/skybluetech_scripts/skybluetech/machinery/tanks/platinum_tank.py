# coding=utf-8
#
from ..basic import RegisterMachine
from .base_tank import BasicTank, RegisterTank


@RegisterMachine
@RegisterTank
class PlatinumTank(BasicTank):
    block_name = "skybluetech:platinum_tank"
    max_fluid_volume = 128000


