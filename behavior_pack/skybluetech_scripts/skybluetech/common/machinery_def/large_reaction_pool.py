# coding=utf-8
from ..define.id_enum import (
    Acid, Alkali, Chemical, ChemicalGas, CommonGas, CommonLiquid, CommonOil, Dusts,
    FilterCakes, FineConcentrates, HotFluid, LargeReactionPool as Pool, RawOres, SortedOres,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import CategoryType, Input, Output
from ..mini_jei.machinery.large_reaction_pool import LargeReactionPoolRecipe
from ..utils.structure_palette import GenerateSimpleStructureTemplate
from .small_chemical_reactor import recipes as small_reactor_recipes

STORE_RF_MAX = 64000
FLUID_INPUT_SLOTS = (0, 1, 3)
FLUID_OUTPUT_SLOTS = (2, 4)
FLUID_SLOT_MAX_VOLUMES = dict.fromkeys(FLUID_INPUT_SLOTS + FLUID_OUTPUT_SLOTS, 8000)
K_BATCH = "st:reaction_pool_batch"
K_RECIPE_ID = "st:reaction_pool_recipe"
K_SURFACE = "st:reaction_pool_surface"

INPUT_WALL = [Pool.FRAME, Pool.IO_ITEM_INPUT, Pool.IO_ENERGY_INPUT, Pool.IO_HEAT_INPUT,
              Pool.IO_FLUID_INPUT_1, Pool.IO_FLUID_INPUT_2, Pool.IO_FLUID_INPUT_3]
OUTPUT_WALL = [Pool.FRAME, Pool.IO_ITEM_OUTPUT, Pool.IO_FLUID_OUTPUT_1, Pool.IO_FLUID_OUTPUT_2]
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {"C": Pool.CAP, "i": INPUT_WALL, "I": INPUT_WALL + [Pool.WINDOW],
     "o": OUTPUT_WALL, "O": OUTPUT_WALL + [Pool.WINDOW]},
    {-1: ["CCC", "CCC", "CCC"], 0: ["i#i", "I.I", "iIi"],
     1: ["oOo", "O.O", "oOo"], 2: ["CCC", "CCC", "CCC"]}, "#",
)

recipes = RecipesCollection(Pool.CONTROLLER)
water = CommonLiquid.WATER
hcl = Chemical.HYDROCHLORIC_ACID
alkali = Alkali.SODIUM_HYDROXIDE_SOLUTION
peroxide = Chemical.PEROXIDE


def _add(key, title, feeds, products, solid_in=None, solid_out=None,
         power=256, ticks=200, heat=(0, 0, 0)):
    inputs = {CategoryType.FLUID: dict((s, Input(*v)) for s, v in zip(FLUID_INPUT_SLOTS, feeds))}
    outputs = {CategoryType.FLUID: dict((s, Output(*v)) for s, v in zip(FLUID_OUTPUT_SLOTS, products))}
    if solid_in:
        inputs[CategoryType.ITEM] = {0: Input(solid_in)}
    if solid_out:
        outputs[CategoryType.ITEM] = {1: Output(*solid_out)}
    recipes.add_recipe(LargeReactionPoolRecipe(key, title, inputs, outputs, power, ticks, heat))


# 旧釜两条配方沿用原槽号和成本，以产品 ID 对应稳定批次名。
_legacy = {HotFluid.MOLTEN_POLYETHYLENE: ("polyethylene", "聚乙烯合成"),
           CommonLiquid.EVIL_UNDEAD: ("evil_undead", "恶灵液配制")}
for old_recipe in small_reactor_recipes:
    product = old_recipe.outputs.get(CategoryType.FLUID, {}).get(2)
    identity = _legacy.get(product.id) if product else None
    if identity:
        recipes.add_recipe(LargeReactionPoolRecipe(
            identity[0], identity[1], old_recipe.inputs, old_recipe.outputs,
            old_recipe.power_cost, old_recipe.tick_duration,
        ))

# 公共供药与回收。PM-R4 与吸收制酸共用一条。
_add("pm_r4", "氯化氢吸收", [(Acid.HYDROGEN_CHLORIDE, 200), (water, 100)], [(hcl, 200)])
_add("v1", "植物油制捕收剂", [(CommonOil.VEGETABLE_OIL, 100), (water, 100)],
     [(Chemical.MINERAL_COLLECTOR, 200)], power=128, ticks=100)
_add("p2", "工艺水高级氧化", [(CommonLiquid.ORGANIC_WASTE, 200), (CommonGas.OXYGEN, 100)],
     [(CommonLiquid.PROCESS_WATER, 200)], ticks=400)
_add("a1", "过氧化氢制备", [(CommonGas.HYDROGEN, 20), (CommonGas.OXYGEN, 20),
                         (CommonLiquid.DISTILLED_WATER, 80)], [(peroxide, 100)], power=128, ticks=100)
_add("c2", "煤焦油制药", [(Chemical.COAL_TAR, 1000), (peroxide, 500), (CommonGas.ETHYLENE, 400)],
     [(Chemical.MINERAL_COLLECTOR, 1600), (CommonOil.FUEL_OIL, 300)], power=512, ticks=400, heat=(400, 450, 2000))
_add("w2", "木杂酚油制药", [(Chemical.WOOD_CREOSOTE, 1000), (peroxide, 200), (CommonGas.ETHYLENE, 200)],
     [(Chemical.MINERAL_COLLECTOR, 800), (CommonOil.FUEL_OIL, 600)], ticks=300, heat=(400, 450, 1000))
_add("w3", "木杂酚油加氢", [(Chemical.WOOD_CREOSOTE, 1000), (CommonGas.HYDROGEN, 200)],
     [(CommonOil.LUBRICANT, 500), (CommonOil.FUEL_OIL, 500)], ticks=300, heat=(450, 500, 1000))
_add("n1", "方解石中和", [(hcl, 800)], [(Chemical.CALCIUM_LIQUOR, 800)], "minecraft:calcite")
_add("n4", "混凝土促凝液配制", [(water, 1000)], [(CommonLiquid.CONCRETE_ACCEL, 1000)], Dusts.CALCIUM_CHLORIDE)


def _leach(key, metal, raw, sorted_ore, fine, reagent, result, fine_heat,
           main_heat=(0, 0, 0), main_power=256, fine_power=256, fine_ticks=200):
    for suffix, title, ore in (("1", "粗矿浸出", raw), ("2", "预选料浸出", sorted_ore)):
        _add(key + suffix, metal + title, [(reagent, 800), (water, 200)],
             [(result, 1000)], ore, power=main_power, heat=main_heat)
    fine_key = "4" if key in ("al", "ti") else "3"
    _add(key + fine_key, metal + "精矿热浸", [(reagent, 200), (water, 50)], [(result, 250)],
         fine, power=fine_power, ticks=fine_ticks, heat=fine_heat)


_leach("fe", "铁", "minecraft:raw_iron", SortedOres.IRON, FineConcentrates.IRON,
       hcl, Chemical.IRON_LEACH, (350, 390, 400))
_add("fe_precipitate", "氢氧化铁沉淀", [(Chemical.IRON_LEACH, 250), (alkali, 100)],
     [(CommonLiquid.DILUTE_BRINE, 200)], solid_out=(FilterCakes.IRON_HYDROXIDE, 1))
_leach("cu", "铜", "minecraft:raw_copper", SortedOres.COPPER, FineConcentrates.COPPER,
       Acid.SULFURIC_ACID, Chemical.COPPER_LEACH, (350, 390, 400))
_leach("ni", "镍", RawOres.NICKEL, SortedOres.NICKEL, FineConcentrates.NICKEL,
       Acid.SULFURIC_ACID, Chemical.NICKEL_LEACH, (380, 420, 400))
for key, title, ore, portions, heat in (
    ("sn1", "粗锡酸洗", RawOres.TIN, 4, (0, 0, 0)), ("sn2", "预选锡料酸洗", SortedOres.TIN, 4, (0, 0, 0)),
    ("sn3", "锡精矿强化酸洗", FineConcentrates.TIN, 1, (350, 390, 400)),
):
    _add(key, title, [(hcl, 200 * portions), (water, 50 * portions)], [(Chemical.TIN_ACID_WASTE, 250 * portions)],
         ore, (Dusts.PURIFIED_CASSITERITE, portions), heat=heat)
_add("snw2", "锡矿废液中和", [(Chemical.TIN_DEACID_WASTE, 100), (alkali, 25)], [(Chemical.TIN_NEUTRAL_LIQ, 125)])
_add("pb6", "铅焙烧尾气吸收", [(ChemicalGas.SULFUR_DIOXIDE, 100), (peroxide, 100)], [(Acid.SULFURIC_ACID, 100)])


def _precious(key, metal, ores, result, oxidant, wash, main_heat, fine_heat):
    for index, suffix in enumerate(("1", "2", "4")):
        fine = index == 2
        scale = 1 if fine else 4
        title = ("粗矿氧化浸出", "预选料氧化浸出", "精矿强化浸出")[index]
        _add(key + suffix, metal + title, [(hcl, (100 if key == "ag" else 200) * scale),
             (peroxide, oxidant * scale), (water, wash * scale)], [(result, 250 * scale)],
             ores[index], power=384 if fine else 512, ticks=200 if fine else 400,
             heat=fine_heat if fine else main_heat)


_precious("ag", "银", (RawOres.SILVER, SortedOres.SILVER, FineConcentrates.SILVER),
          Chemical.SILVER_SLURRY, 50, 100, (330, 350, 400), (350, 370, 400))
_precious("au", "金", ("minecraft:raw_gold", SortedOres.GOLD, FineConcentrates.GOLD),
          Chemical.GOLD_LEACH, 50, 50, (340, 360, 400), (360, 380, 400))
_precious("pt", "铂", (RawOres.PLATINUM, SortedOres.PLATINUM, FineConcentrates.PLATINUM),
          Chemical.PLATINUM_LEACH, 100, 50, (350, 370, 400), (370, 390, 400))
_add("au5", "氯金液净化", [(Chemical.GOLD_LEACH, 250), (water, 50)], [(Chemical.GOLD_SOLUTION, 250), (Chemical.BARREN_HCL, 50)])
_add("pt5", "氯铂液净化", [(Chemical.PLATINUM_LEACH, 250), (water, 50)], [(Chemical.PLATINUM_SOLUTION, 250), (Chemical.BARREN_HCL, 50)])
_leach("al", "铝", RawOres.ALUMINUM, SortedOres.ALUMINUM, FineConcentrates.ALUMINUM,
       alkali, Chemical.ALUMINATE, (450, 500, 500), (420, 470, 1600), 160, 200, 100)
_add("al5", "铝酸盐晶种分解", [(Chemical.ALUMINATE, 250), (water, 100)], [(Chemical.ALKALI_LIQUOR, 250)],
     solid_out=(FilterCakes.ALUMINUM_HYDROXIDE, 1), power=120, ticks=100)
_leach("ti", "钛", RawOres.TITANIUM, SortedOres.TITANIUM, FineConcentrates.TITANIUM,
       Acid.CONCENTRATED_SULFURIC_ACID, Chemical.TITANYL_LEACH, (460, 510, 600), (430, 480, 2000), 200, 240, 100)
_add("ti5", "硫酸氧钛水解", [(Chemical.TITANYL_LEACH, 250), (water, 100)], [(Chemical.TITANIUM_ACID, 250)],
     solid_out=(FilterCakes.HYDRATED_TITANIUM_OXIDE, 1), power=160, ticks=100, heat=(360, 390, 300))
_add("mg1", "海水沉镁", [(Chemical.RAW_SEAWATER, 1000), (alkali, 100)], [(CommonLiquid.DILUTE_BRINE, 1000)],
     solid_out=(FilterCakes.MAGNESIUM_HYDROXIDE, 1), power=120, ticks=100)
_add("mg2", "镁滤饼氯化", [(hcl, 200)], [(Chemical.MGCL2_SOLUTION, 250), (water, 50)],
     FilterCakes.MAGNESIUM_HYDROXIDE, power=120, ticks=100)

RECIPES_BY_ID = dict((recipe.recipe_id, recipe) for recipe in recipes)
