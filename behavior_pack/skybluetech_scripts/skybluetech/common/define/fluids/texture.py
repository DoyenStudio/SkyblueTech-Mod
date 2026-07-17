from ..id_enum import fluids
from .define import BasicFluidTexture, FluidTexture

AIR = BasicFluidTexture("textures/fluid/gas", 1)
WATER = BasicFluidTexture("textures/fluid/basic_water_static", 32, 2)
WATER_VAPOR = BasicFluidTexture("textures/fluid/water_vapor", 1)
LAVA = BasicFluidTexture("textures/fluid/gray_lava_static", 20, 5)
MOLTEN_METAL = BasicFluidTexture("textures/fluid/gray_molten_metal_static", 49, 5)
VANILLA_WATER = BasicFluidTexture("textures/fluid/water_static", 32, 2)
VANILLA_LAVA = BasicFluidTexture("textures/fluid/lava_static", 20, 16)
DEEPSLATE_LAVA = BasicFluidTexture("textures/fluid/deepslate_lava_static", 20, 5)
METHANE_MUD = BasicFluidTexture("textures/fluid/methane_mud", 1)
BASIC_FLUID = BasicFluidTexture("textures/fluid/basic_fluid", 1)

BASIC_FLUID_TEXTURE = FluidTexture((255, 255, 255), 255, BASIC_FLUID)

FLUID_COLORS_AND_TEXTURES = {
    fluids.CommonLiquid.DISTILLED_WATER: FluidTexture((0, 229, 255), 128, WATER),
    fluids.CommonGas.COMPRESSED_AIR: FluidTexture((240, 240, 240), 64, AIR),
    fluids.CommonGas.HYDROGEN: FluidTexture((220, 240, 255), 64, AIR),
    fluids.CommonGas.METHANE: FluidTexture((255, 240, 200), 64, AIR),
    fluids.CommonGas.WATER_VAPOR: FluidTexture((240, 240, 255), 64, WATER_VAPOR),
    fluids.CommonOil.LUBRICANT: FluidTexture((255, 207, 0), 192, WATER),
    fluids.CommonOil.RAW_OIL: FluidTexture((44, 39, 28), 255, WATER),
    fluids.CommonOil.VEGETABLE_OIL: FluidTexture((170, 255, 0), 192, WATER),
    fluids.Acid.SULFURIC_ACID: FluidTexture((255, 216, 216), 128, WATER),
    fluids.Acid.CONCENTRATED_SULFURIC_ACID: FluidTexture((255, 216, 216), 128, WATER),
    fluids.Acid.SO3: FluidTexture((255, 216, 216), 128, WATER),
    fluids.DeepLava.HEAVY_LAVA: FluidTexture((168, 36, 36), 255, LAVA),
    fluids.DeepLava.LIGHT_LAVA: FluidTexture((255, 60, 0), 255, LAVA),
    fluids.DeepLava.MID_LAVA: FluidTexture((255, 0, 0), 255, LAVA),
    fluids.Molten.COPPER: FluidTexture((231, 124, 86), 255, MOLTEN_METAL),
    fluids.Molten.EARTH: FluidTexture((127, 54, 0), 255, LAVA),
    fluids.Molten.GOLD: FluidTexture((255, 255, 0), 255, MOLTEN_METAL),
    fluids.Molten.IMPURITY: FluidTexture((74, 47, 21), 255, LAVA),
    fluids.Molten.IRON: FluidTexture((200, 200, 200), 255, MOLTEN_METAL),
    fluids.Molten.LEAD: FluidTexture((163, 153, 229), 255, MOLTEN_METAL),
    fluids.Molten.NICKEL: FluidTexture((197, 197, 145), 255, MOLTEN_METAL),
    fluids.Molten.PLATINUM: FluidTexture((158, 235, 255), 255, MOLTEN_METAL),
    fluids.Molten.SILVER: FluidTexture((239, 248, 249), 255, MOLTEN_METAL),
    fluids.Molten.TIN: FluidTexture((233, 233, 233), 255, MOLTEN_METAL),
    # Vanilla
    fluids.Vanilla.WATER: FluidTexture((255, 255, 255), 128, VANILLA_WATER),
    fluids.Vanilla.LAVA: FluidTexture((255, 255, 255), 255, VANILLA_LAVA),
    # color-special
    fluids.DeepLava.DEEPSLATE_LAVA: FluidTexture((255, 255, 255), 255, DEEPSLATE_LAVA),
    fluids.CommonLiquid.METHANE_MUD: FluidTexture((255, 255, 255), 255, METHANE_MUD),
}


def GetFluidTexture(fluid_id):
    # type: (str) -> FluidTexture
    return FLUID_COLORS_AND_TEXTURES.get(fluid_id, BASIC_FLUID_TEXTURE)


def RegisterFluidTexture(fluid_id, basic_texture, rgb=(255, 255, 255), alpha=255):
    # type: (str, BasicFluidTexture, tuple[int, int, int], int) -> None
    FLUID_COLORS_AND_TEXTURES[fluid_id] = FluidTexture(rgb, alpha, basic_texture)
