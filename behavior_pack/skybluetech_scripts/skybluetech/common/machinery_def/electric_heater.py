# coding=utf-8
from ..utils.phys_math import Thermal

K_MAX_POWER = "max_power"
"玩家设定的最大功率, 单位 RF/t; 决定本机的产热速率与耗电"

K_KELVIN_LIMIT = "kelvin_limit"
"玩家设定的目标温度, 单位 K"

K_CURRENT_POWER = "current_power"
"本机当前的实际功率(按实际产热折算), 单位 RF/t, 仅供 UI 显示"

STORE_RF_MAX = 64000
"本机最大储电量, 单位 RF"

MAX_HEAT_VALUE = 500
"本机相对环境温度的温升上限, 单位 K"

MIN_KELVIN = int(Thermal.STD_ENV_KELVIN)
"可设定的最低温度, 即环境温度, 单位 K"

MAX_KELVIN = MIN_KELVIN + MAX_HEAT_VALUE
"可设定的最高温度, 单位 K"

MAX_POWER = STORE_RF_MAX
"可设定的最大功率上限, 单位 RF/t; 与重构前的上限保持一致"

# 电→热单价不在本文件定义: 它是全包的标准量, 见 `Thermal.ELECTRIC_PER_HEAT`
# (common/utils/phys_math.py) 与 `HeatCtrl.electric_per_heat`。取 10 时 1 RF/t 的电
# 对应每周期 `heat_power = 0.5`(1 RF/t ÷ 10 × `HeatCtrl.WORK_INTERVAL`), 配合
# `HeatCtrl.env_conductance = 0.002` 可得约 50K 的稳态温升。
