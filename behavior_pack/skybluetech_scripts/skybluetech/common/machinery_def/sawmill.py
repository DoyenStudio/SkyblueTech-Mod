# coding=utf-8
from ..define import id_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.sawmill import (
    MachineRecipe,
    SawmillRecipe,
    Input,
    Output,
)

STORE_RF_MAX = 8800

POWER_COST = 20
TICK_DURATION = 160


def _log_recipe(log_id, planks_id):
    # type: (str, str) -> SawmillRecipe
    return SawmillRecipe(
        Input(log_id),
        {1: Output(planks_id, 6), 2: Output(id_enum.Dusts.SAWDUST, 1, prob=0.2)},
        POWER_COST,
        TICK_DURATION,
    )


def _plank_recipe(planks_id):
    # type: (str) -> SawmillRecipe
    return SawmillRecipe(
        Input(planks_id),
        {1: Output("minecraft:stick", 3)},
        POWER_COST,
        TICK_DURATION,
    )


recipes = RecipesCollection(
    id_enum.Machinery.SAWMILL,
    # 主世界原木 -> 对应木板
    _log_recipe("minecraft:oak_log", "minecraft:oak_planks"),
    _log_recipe("minecraft:spruce_log", "minecraft:spruce_planks"),
    _log_recipe("minecraft:birch_log", "minecraft:birch_planks"),
    _log_recipe("minecraft:jungle_log", "minecraft:jungle_planks"),
    _log_recipe("minecraft:acacia_log", "minecraft:acacia_planks"),
    _log_recipe("minecraft:dark_oak_log", "minecraft:dark_oak_planks"),
    _log_recipe("minecraft:mangrove_log", "minecraft:mangrove_planks"),
    _log_recipe("minecraft:cherry_log", "minecraft:cherry_planks"),
    _log_recipe("minecraft:pale_oak_log", "minecraft:pale_oak_planks"),
    _log_recipe("minecraft:bamboo_block", "minecraft:bamboo_planks"),
    # 去皮原木 -> 对应木板
    _log_recipe("minecraft:stripped_oak_log", "minecraft:oak_planks"),
    _log_recipe("minecraft:stripped_spruce_log", "minecraft:spruce_planks"),
    _log_recipe("minecraft:stripped_birch_log", "minecraft:birch_planks"),
    _log_recipe("minecraft:stripped_jungle_log", "minecraft:jungle_planks"),
    _log_recipe("minecraft:stripped_acacia_log", "minecraft:acacia_planks"),
    _log_recipe("minecraft:stripped_dark_oak_log", "minecraft:dark_oak_planks"),
    _log_recipe("minecraft:stripped_mangrove_log", "minecraft:mangrove_planks"),
    _log_recipe("minecraft:stripped_cherry_log", "minecraft:cherry_planks"),
    _log_recipe("minecraft:stripped_pale_oak_log", "minecraft:pale_oak_planks"),
    _log_recipe("minecraft:stripped_bamboo_block", "minecraft:bamboo_planks"),
    # 下界菌柄 -> 对应木板
    _log_recipe("minecraft:crimson_stem", "minecraft:crimson_planks"),
    _log_recipe("minecraft:warped_stem", "minecraft:warped_planks"),
    _log_recipe("minecraft:stripped_crimson_stem", "minecraft:crimson_planks"),
    _log_recipe("minecraft:stripped_warped_stem", "minecraft:warped_planks"),
    # 木板 -> 木棍
    _plank_recipe("minecraft:oak_planks"),
    _plank_recipe("minecraft:spruce_planks"),
    _plank_recipe("minecraft:birch_planks"),
    _plank_recipe("minecraft:jungle_planks"),
    _plank_recipe("minecraft:acacia_planks"),
    _plank_recipe("minecraft:dark_oak_planks"),
    _plank_recipe("minecraft:mangrove_planks"),
    _plank_recipe("minecraft:cherry_planks"),
    _plank_recipe("minecraft:pale_oak_planks"),
    _plank_recipe("minecraft:bamboo_planks"),
    _plank_recipe("minecraft:crimson_planks"),
    _plank_recipe("minecraft:warped_planks"),
    _plank_recipe("minecraft:bamboo_mosaic"),
)  # type: RecipesCollection[MachineRecipe]
