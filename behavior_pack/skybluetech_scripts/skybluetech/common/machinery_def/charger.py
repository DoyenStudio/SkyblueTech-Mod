# coding=utf-8
from ..define.id_enum import Machinery, DEACTIVATION_REDSTONE
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.charger import MachineRecipe, gen_preset_recipe

K_CHARGE_RF = "st:charge_rf"
K_CHARGE_RF_MAX = "st:charge_rf_max"

CHARGE_SPEED = 64
STORE_RF_MAX = 10000

# 惰性红石 -> 红石粉: 红石发电机烧一块惰性红石可发电 160 RF/t × 10t = 1600 RF,
# 反向充能合成按该总发电量的 125% 计, 即 1600 × 1.25 / 8 = 250 RF/t, 8 ticks 跑完。
DEFAULT_POWER = 250
DEFAULT_TICK_DURATION = 8

preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)


recipes = RecipesCollection(
    Machinery.CHARGER,
    preset(DEACTIVATION_REDSTONE, 1, "minecraft:redstone", 1),
)  # type: RecipesCollection[MachineRecipe]
