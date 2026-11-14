# coding=utf-8
STORE_RF_MAX = 8800
POWER_PER_LEVEL = 10
MIN_WIND_RANGE = 10.0
MAX_WIND_RANGE = 20.0
MAX_REDSTONE_STRENGTH = 15
TICKS_PER_SECOND = 20.0

K_REDSTONE_STRENGTH = "redstone_strength"
K_ANIM_SPEED = "fan_speed"


def get_wind_range(strength):
    # type: (int) -> float
    if strength <= 0:
        return 0.0
    return MIN_WIND_RANGE + (MAX_WIND_RANGE - MIN_WIND_RANGE) * (
        strength - 1
    ) / (MAX_REDSTONE_STRENGTH - 1)
