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
    fluids.CommonLiquid.DISTILLED_WATER: BasicFluidTexture("textures/fluid/baked/skybluetech.distilled_water/static", 32, 2),
    fluids.CommonGas.COMPRESSED_AIR: BasicFluidTexture("textures/fluid/baked/skybluetech.compressed_air/ui", 32, 2),
    fluids.CommonGas.HYDROGEN: BasicFluidTexture("textures/fluid/baked/skybluetech.hydrogen/ui", 32, 2),
    fluids.CommonGas.NITROGEN: BasicFluidTexture("textures/fluid/baked/skybluetech.nitrogen/ui", 32, 2),
    fluids.CommonGas.METHANE: BasicFluidTexture("textures/fluid/baked/skybluetech.methane/ui", 32, 2),
    fluids.CommonGas.WATER_VAPOR: BasicFluidTexture("textures/fluid/baked/skybluetech.water_vapor/static", 1, 1),
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
}


def GetFluidTexture(fluid_id):
    # type: (str) -> BasicFluidTexture
    return FLUID_TEXTURES.get(fluid_id, BASIC_FLUID)


def RegisterFluidTexture(fluid_id, basic_texture):
    # type: (str, BasicFluidTexture) -> None
    FLUID_TEXTURES[fluid_id] = basic_texture
