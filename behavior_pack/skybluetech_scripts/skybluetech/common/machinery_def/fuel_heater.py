# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.thermal_generator import (
    FUEL_SECONDS_MAP,
    K_BURN_SEC_LEFT,
    K_MAX_BURN_SEC,
    TICK_POWER,
)

MIN_KELVIN = 300
MAX_KELVIN = 900
MAX_HEAT_VALUE = MAX_KELVIN - MIN_KELVIN

FUEL_HEAT_MULTIPLIER = 4.0
"同种燃料经火力发电机、电力加热仓转换后所得热量的倍率。"

SECOND_PER_TICK = 0.05
