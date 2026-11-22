# coding=utf-8
from ..define.id_enum import Machinery
from ..define.id_enum.fluids import Acid, Alkali, Chemical, CommonLiquid
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.effluent_outfall import EffluentOutfallRecipe


recipes = RecipesCollection(
    Machinery.EFFLUENT_OUTFALL,
    EffluentOutfallRecipe(CommonLiquid.WATER, biome_group="any"),
    EffluentOutfallRecipe(CommonLiquid.DISTILLED_WATER, biome_group="any"),
    EffluentOutfallRecipe(Chemical.HYDROCHLORIC_ACID, volume_per_second=2, biome_group="river_ocean"),
    EffluentOutfallRecipe(Acid.SULFURIC_ACID, volume_per_second=2, biome_group="river_ocean"),
    EffluentOutfallRecipe(Alkali.SODIUM_HYDROXIDE_SOLUTION, volume_per_second=2, biome_group="river_ocean"),
    EffluentOutfallRecipe(Chemical.TIN_DEACID_WASTE, volume_per_second=40, biome_group="river_ocean"),
    EffluentOutfallRecipe(CommonLiquid.PROCESS_WATER, volume_per_second=2000, biome_group="water"),
    EffluentOutfallRecipe(CommonLiquid.DILUTE_BRINE, volume_per_second=2000, biome_group="river_ocean"),
    EffluentOutfallRecipe(CommonLiquid.BRINE, volume_per_second=2000, biome_group="river_ocean"),
    EffluentOutfallRecipe(CommonLiquid.SATURATED_BRINE, volume_per_second=2000, biome_group="river_ocean"),
    EffluentOutfallRecipe(Chemical.RAW_SEAWATER, volume_per_second=2000, biome_group="river_ocean"),
)


def classify_biome(biome_name):
    # Bedrock 海洋变种包括 deep_lukewarm_ocean、legacy_frozen_ocean 等。
    name = (biome_name or "").split(":")[-1]
    if "ocean" in name.split("_") or name in ("river", "frozen_river"):
        return "river_ocean"
    if name in ("swamp", "swampland", "swampland_mutated", "mangrove_swamp"):
        return "water"
    return "land"


def find_recipe(fluid_id, biome):
    for recipe in recipes:
        if recipe.fluid_id != fluid_id:
            continue
        group = recipe.biome_group
        if (group == "any" or group == biome
                or (group == "water" and biome == "river_ocean")):
            return recipe
    return None
