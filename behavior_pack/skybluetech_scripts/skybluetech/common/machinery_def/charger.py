# coding=utf-8
from ..define.id_enum import (
    Machinery,
    DEACTIVATION_REDSTONE,
    DEACTIVATION_REDSTONE_BLOCK,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.charger import MachineRecipe, gen_preset_recipe

K_CHARGE_RF = "st:charge_rf"
K_CHARGE_RF_MAX = "st:charge_rf_max"

CHARGE_SPEED = 64
STORE_RF_MAX = 10000

# 反向充能按红石发电量的 125% 耗电：1600 RF × 1.25 = 2000 RF。
DEFAULT_POWER = 250
DEFAULT_TICK_DURATION = 8

preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
# 一块相当于九份红石粉，按同样的功率处理九倍时长。
block_preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION * 9)


recipes = RecipesCollection(
    Machinery.CHARGER,
    preset(DEACTIVATION_REDSTONE, 1, "minecraft:redstone", 1),
    block_preset(DEACTIVATION_REDSTONE_BLOCK, 1, "minecraft:redstone_block", 1),
)  # type: RecipesCollection[MachineRecipe]
