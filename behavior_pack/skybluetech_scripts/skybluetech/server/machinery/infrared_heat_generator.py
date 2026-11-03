# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.infrared_heat_generator import (
    MAX_HEAT_VALUE,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.electric_heater import ElectricHeater


@RegisterMachine
class InfraredHeatGenerator(ElectricHeater):
    "红外高热发生器, 沿用电力加热仓的供电、控温和操作事件。"

    block_name = Machinery.INFRARED_HEAT_GENERATOR
    max_heat_value = MAX_HEAT_VALUE
