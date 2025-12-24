# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..basic import RegisterMachine
from .base_tank import BasicTank, RegisterTank

INFINITY = float("inf")


@RegisterMachine
@RegisterTank
class BronzeTank(BasicTank):
    block_name = "skybluetech:bronze_tank"
    max_fluid_volume = 32000


