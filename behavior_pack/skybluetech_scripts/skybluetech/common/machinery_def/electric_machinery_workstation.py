# coding=utf-8
from ..define.id_enum import Ingots, Machinery
from ..mini_jei.core import RecipesCollection
from .macerator import STORE_RF_MAX
from .machinery_workstation import recipes as workstation_recipes

DEFAULT_POWER = 120
CRAFT_TICKS_MULTIPLIER = 5
SOLDER_SLOT = 9
OUTPUT_SLOT = 10
SOLDER_ITEM_ID = Ingots.SOLDERING
K_OUTPUT_ITEM_ID = "st:electric_workstation_output"
K_SELECTED_RECIPE = "st:electric_workstation_selected_recipe"

# 电动版直接复用机件加工台的配方: 焊锡要求、产物槽(10)与工艺时长/耗能都在机器侧处理
recipes = RecipesCollection(
    Machinery.ELECTRIC_MACHINERY_WORKSTATION, *workstation_recipes
)
