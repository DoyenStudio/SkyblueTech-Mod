# coding=utf-8
#
from ..basic import RegisterMachine
from .base_tank import BasicTank, RegisterTank


@RegisterMachine
@RegisterTank
class InvarTank(BasicTank):
    block_name = "skybluetech:invar_tank"
    max_fluid_volume = 40000


