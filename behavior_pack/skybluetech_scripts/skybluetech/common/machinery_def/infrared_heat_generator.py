# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.electric_heater import (
    MIN_KELVIN,
)

MAX_KELVIN = 2300
"可设定的最高温度, 单位 K"

MAX_HEAT_VALUE = MAX_KELVIN - MIN_KELVIN
"本机相对环境温度的温升上限, 单位 K"
