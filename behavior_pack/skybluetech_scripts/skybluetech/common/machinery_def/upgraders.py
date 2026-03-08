# coding=utf-8
from ...common.define.id_enum.items import Upgraders

# 速度提升倍率 (原 1.0, 累加)
SPEED_POSITIVE = {
    Upgraders.BASIC_SPEED_UPGRADER: 0.5,
}
# 速度衰减倍率 (原 1.0, 累加)
SPEED_NEGATIVE = {
    Upgraders.GENERIC_EXPANSION_UPGRADER: 0.3,
}
# 能量消耗提升倍率 (原 1.0, 累加)
POWER_POSITIVE = {
    Upgraders.BASIC_SPEED_UPGRADER: 0.7,
    Upgraders.GENERIC_EXPANSION_UPGRADER: 0.4,
}
# 能量消耗衰减倍率 (原 1.0, 累加)
POWER_NEGATIVE = {
    Upgraders.BASIC_ENERGY_UPGRADER: 0.2,
}
