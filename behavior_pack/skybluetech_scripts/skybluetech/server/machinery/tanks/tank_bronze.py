# coding=utf-8
from ..basic import RegisterMachine
from .base_tank import BasicTank, RegisterTank

INFINITY = float("inf")


@RegisterMachine
@RegisterTank
class BronzeTank(BasicTank):
    block_name = "skybluetech:tank_bronze"
    max_fluid_volume = 32000
