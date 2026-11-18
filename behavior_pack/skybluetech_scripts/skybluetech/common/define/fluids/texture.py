from ..id_enum import fluids
from .define import BasicFluidTexture

AIR = BasicFluidTexture("textures/fluid/gas_static", 32, 2)
WATER = BasicFluidTexture("textures/fluid/basic_water_static", 32, 2)
WATER_VAPOR = BasicFluidTexture("textures/fluid/water_vapor", 1)
LAVA = BasicFluidTexture("textures/fluid/gray_lava_static", 20, 5)
MOLTEN_METAL = BasicFluidTexture("textures/fluid/gray_molten_metal_static", 49, 5)
VANILLA_WATER = BasicFluidTexture("textures/fluid/water_static", 32, 2)
VANILLA_LAVA = BasicFluidTexture("textures/fluid/lava_static", 20, 16)
DEEPSLATE_LAVA = BasicFluidTexture("textures/fluid/deepslate_lava_static", 20, 5)
METHANE_MUD = BasicFluidTexture("textures/fluid/methane_mud", 1)
BASIC_FLUID = BasicFluidTexture("textures/fluid/basic_fluid", 1)
LIQUID_RESIN_STATIC = BasicFluidTexture("textures/fluid/liquid_resin_static", 39, 2)

FLUID_TEXTURES = {
    fluids.CommonGas.ARGON: BasicFluidTexture("textures/fluid/baked/skybluetech.argon/static", 32, 2),
    fluids.Acid.HYDROGEN_CHLORIDE: BasicFluidTexture("textures/fluid/baked/skybluetech.hydrogen_chloride/static", 32, 2),
    fluids.Molten.PALLADIUM: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_palladium/static", 49, 5),
    fluids.Molten.ROSIN: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_rosin/static", 32, 2),
    fluids.CommonLiquid.DISTILLED_WATER: BasicFluidTexture("textures/fluid/baked/skybluetech.distilled_water/static", 32, 2),
    fluids.CommonGas.COMPRESSED_AIR: BasicFluidTexture("textures/fluid/baked/skybluetech.compressed_air/ui", 32, 2),
    fluids.CommonGas.HYDROGEN: BasicFluidTexture("textures/fluid/baked/skybluetech.hydrogen/ui", 32, 2),
    fluids.CommonGas.NITROGEN: BasicFluidTexture("textures/fluid/baked/skybluetech.nitrogen/ui", 32, 2),
    fluids.CommonGas.METHANE: BasicFluidTexture("textures/fluid/baked/skybluetech.methane/ui", 32, 2),
    fluids.CommonGas.WATER_VAPOR: BasicFluidTexture("textures/fluid/baked/skybluetech.water_vapor/static", 32, 2),
    fluids.CommonOil.LUBRICANT: BasicFluidTexture("textures/fluid/baked/skybluetech.lubricant/static", 32, 2),
    fluids.CommonOil.RAW_OIL: BasicFluidTexture("textures/fluid/baked/skybluetech.raw_oil/static", 32, 2),
    fluids.CommonOil.VEGETABLE_OIL: BasicFluidTexture("textures/fluid/baked/skybluetech.vegetable_oil/static", 32, 2),
    fluids.Acid.SULFURIC_ACID: BasicFluidTexture("textures/fluid/baked/skybluetech.sulfuric_acid/static", 32, 2),
    fluids.Acid.CONCENTRATED_SULFURIC_ACID: BasicFluidTexture("textures/fluid/baked/skybluetech.concentrated_sulfuric_acid/static", 32, 2),
    fluids.Acid.SO3: BasicFluidTexture("textures/fluid/baked/skybluetech.so3/static", 32, 2),
    fluids.DeepLava.HEAVY_LAVA: BasicFluidTexture("textures/fluid/baked/skybluetech.heavy_lava/static", 20, 5),
    fluids.DeepLava.LIGHT_LAVA: BasicFluidTexture("textures/fluid/baked/skybluetech.light_lava/static", 20, 5),
    fluids.DeepLava.MID_LAVA: BasicFluidTexture("textures/fluid/baked/skybluetech.mid_lava/static", 20, 5),
    fluids.Molten.COPPER: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_copper/static", 49, 5),
    fluids.Molten.EARTH: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_earth/static", 20, 5),
    fluids.Molten.GOLD: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_gold/static", 49, 5),
    fluids.Molten.IMPURITY: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_impurity/static", 20, 5),
    fluids.Molten.IRON: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_iron/static", 49, 5),
    fluids.Molten.LEAD: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_lead/static", 49, 5),
    fluids.Molten.NICKEL: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_nickel/static", 49, 5),
    fluids.Molten.PLATINUM: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_platinum/static", 49, 5),
    fluids.Molten.SILVER: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_silver/static", 49, 5),
    fluids.Molten.TIN: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_tin/static", 49, 5),
    # Vanilla
    fluids.Vanilla.WATER: BasicFluidTexture("textures/fluid/baked/minecraft.water/ui", 32, 2),
    fluids.Vanilla.LAVA: BasicFluidTexture("textures/fluid/baked/minecraft.lava/ui", 20, 16),
    # color-special
    fluids.DeepLava.DEEPSLATE_LAVA: BasicFluidTexture("textures/fluid/baked/skybluetech.deepslate_lava/flowing_block_static", 20, 5),
    fluids.CommonLiquid.METHANE_MUD: BasicFluidTexture("textures/fluid/baked/skybluetech.methane_mud/static", 1, 1),
    fluids.CommonLiquid.LIQUID_AIR: BasicFluidTexture("textures/fluid/baked/skybluetech.liquid_air/static", 1, 1),
    fluids.CommonLiquid.LIQUID_RESIN: BasicFluidTexture("textures/fluid/baked/skybluetech.liquid_resin/static", 39, 2),
    fluids.CommonGas.OXYGEN: BasicFluidTexture("textures/fluid/baked/skybluetech.oxygen/static", 32, 2),
    fluids.CommonLiquid.BRINE: BasicFluidTexture("textures/fluid/baked/skybluetech.brine/static", 32, 2),
    fluids.CommonLiquid.SATURATED_BRINE: BasicFluidTexture("textures/fluid/baked/skybluetech.saturated_brine/static", 32, 2),
    fluids.CommonGas.CHLORINE: BasicFluidTexture("textures/fluid/baked/skybluetech.chlorine/static", 32, 2),
    fluids.Alkali.SODIUM_HYDROXIDE_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.sodium_hydroxide_solution/static", 32, 2),
    fluids.CommonLiquid.DILUTE_BRINE: BasicFluidTexture("textures/fluid/baked/skybluetech.dilute_brine/static", 32, 2),
    fluids.CommonGas.ETHYLENE: BasicFluidTexture("textures/fluid/baked/skybluetech.ethylene/static", 32, 2),
    fluids.CommonGas.PURE_METHANE: BasicFluidTexture("textures/fluid/baked/skybluetech.pure_methane/static", 32, 2),
    fluids.HotFluid.MOLTEN_POLYETHYLENE: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_polyethylene/static", 39, 2),
    fluids.CommonOil.TREE_OIL: BasicFluidTexture("textures/fluid/baked/skybluetech.tree_oil/static", 39, 2),
    fluids.CommonLiquid.EVIL_UNDEAD: BasicFluidTexture("textures/fluid/baked/skybluetech.evil_undead/static", 32, 2),
    fluids.Chemical.MINERAL_COLLECTOR: BasicFluidTexture("textures/fluid/baked/skybluetech.mineral_collector/static", 32, 2),
    fluids.Chemical.COAL_TAR: BasicFluidTexture("textures/fluid/baked/skybluetech.coal_tar/static", 39, 2),
    fluids.Chemical.WOOD_CREOSOTE: BasicFluidTexture("textures/fluid/baked/skybluetech.wood_creosote/static", 39, 2),
    fluids.CommonOil.FUEL_OIL: BasicFluidTexture("textures/fluid/baked/skybluetech.fuel_oil/static", 32, 2),
    fluids.Chemical.FLOTATION_WASTE: BasicFluidTexture("textures/fluid/baked/skybluetech.flotation_waste/static", 32, 2),
    fluids.CommonLiquid.ORGANIC_WASTE: BasicFluidTexture("textures/fluid/baked/skybluetech.organic_waste/static", 32, 2),
    fluids.Chemical.HYDROCHLORIC_ACID: BasicFluidTexture("textures/fluid/baked/skybluetech.hydrochloric_acid/static", 32, 2),
    fluids.Chemical.IRON_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.iron_leach/static", 32, 2),
    fluids.CommonLiquid.PROCESS_WATER: BasicFluidTexture("textures/fluid/baked/skybluetech.process_water/static", 32, 2),
    fluids.Chemical.PEROXIDE: BasicFluidTexture("textures/fluid/baked/skybluetech.peroxide/static", 32, 2),
    fluids.Chemical.CALCIUM_LIQUOR: BasicFluidTexture("textures/fluid/baked/skybluetech.calcium_liquor/static", 32, 2),
    fluids.CommonLiquid.CALCIUM_CHLORIDE: BasicFluidTexture("textures/fluid/baked/skybluetech.calcium_chloride/static", 32, 2),
    fluids.CommonLiquid.CONCRETE_ACCEL: BasicFluidTexture("textures/fluid/baked/skybluetech.concrete_accel/static", 32, 2),
    fluids.Chemical.TIN_ACID_WASTE: BasicFluidTexture("textures/fluid/baked/skybluetech.tin_acid_waste/static", 32, 2),
    fluids.Chemical.TIN_DEACID_WASTE: BasicFluidTexture("textures/fluid/baked/skybluetech.tin_deacid_waste/static", 32, 2),
    fluids.Chemical.TIN_NEUTRAL_LIQ: BasicFluidTexture("textures/fluid/baked/skybluetech.tin_neutral_liq/static", 32, 2),
    fluids.ChemicalGas.SULFUR_DIOXIDE: BasicFluidTexture("textures/fluid/baked/skybluetech.sulfur_dioxide/static", 32, 2),
    fluids.Chemical.COPPER_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.copper_leach/static", 32, 2),
    fluids.Chemical.COPPER_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.copper_solution/static", 32, 2),
    fluids.Chemical.NICKEL_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.nickel_leach/static", 32, 2),
    fluids.Chemical.NICKEL_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.nickel_solution/static", 32, 2),
    fluids.Chemical.SILVER_SLURRY: BasicFluidTexture("textures/fluid/baked/skybluetech.silver_slurry/static", 32, 2),
    fluids.Chemical.GOLD_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.gold_leach/static", 32, 2),
    fluids.Chemical.GOLD_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.gold_solution/static", 32, 2),
    fluids.Chemical.PLATINUM_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.platinum_leach/static", 32, 2),
    fluids.Chemical.PLATINUM_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.platinum_solution/static", 32, 2),
    fluids.Chemical.BARREN_HCL: BasicFluidTexture("textures/fluid/baked/skybluetech.barren_hcl/static", 32, 2),
    fluids.Chemical.ALUMINATE: BasicFluidTexture("textures/fluid/baked/skybluetech.aluminate/static", 32, 2),
    fluids.Chemical.ALKALI_LIQUOR: BasicFluidTexture("textures/fluid/baked/skybluetech.alkali_liquor/static", 32, 2),
    fluids.Chemical.TITANYL_LEACH: BasicFluidTexture("textures/fluid/baked/skybluetech.titanyl_leach/static", 32, 2),
    fluids.Chemical.TITANIUM_ACID: BasicFluidTexture("textures/fluid/baked/skybluetech.titanium_acid/static", 32, 2),
    fluids.Chemical.CRUDE_TICL4: BasicFluidTexture("textures/fluid/baked/skybluetech.crude_ticl4/static", 32, 2),
    fluids.Chemical.PURE_TICL4: BasicFluidTexture("textures/fluid/baked/skybluetech.pure_ticl4/static", 32, 2),
    fluids.Chemical.RAW_SEAWATER: BasicFluidTexture("textures/fluid/baked/skybluetech.raw_seawater/static", 32, 2),
    fluids.Chemical.MGCL2_SOLUTION: BasicFluidTexture("textures/fluid/baked/skybluetech.mgcl2_solution/static", 32, 2),
    fluids.Chemical.MOLTEN_MGCL2: BasicFluidTexture("textures/fluid/baked/skybluetech.molten_mgcl2/static", 49, 5),
    fluids.ChemicalGas.ACID_VAPOR: BasicFluidTexture("textures/fluid/baked/skybluetech.acid_vapor/static", 32, 2),
    fluids.ChemicalGas.CARBON_DIOXIDE: BasicFluidTexture("textures/fluid/baked/skybluetech.carbon_dioxide/static", 32, 2),
}


def GetFluidTexture(fluid_id):
    # type: (str) -> BasicFluidTexture
    return FLUID_TEXTURES.get(fluid_id, BASIC_FLUID)


def RegisterFluidTexture(fluid_id, basic_texture):
    # type: (str, BasicFluidTexture) -> None
    FLUID_TEXTURES[fluid_id] = basic_texture
