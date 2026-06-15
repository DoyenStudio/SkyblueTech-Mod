from ..id_enum import fluids


FLUID_COLORS_AND_TEXTURES = {
    fluids.Common.COMPRESSED_AIR: ((240, 240, 240), 4),
    fluids.Common.DISTILLED_WATER: ((0, 229, 255), 3),
    fluids.DeepLava.HEAVY_LAVA: ((168, 36, 36), 0),
    fluids.Common.HYDROGEN: ((220, 240, 255), 4),
    fluids.DeepLava.LIGHT_LAVA: ((255, 60, 0), 0),
    fluids.DeepLava.MID_LAVA: ((255, 0, 0), 0),
    fluids.Common.METHANE: ((255, 240, 200), 4),
    fluids.Common.LUBRICANT: ((255, 207, 0), 3),
    fluids.Common.RAW_OIL: ((44, 39, 28), 3),
    fluids.Common.VEGETABLE_OIL: ((170, 255, 0), 3),
    fluids.Acid.SULFURIC_ACID: ((255, 216, 216), 3),
    fluids.Molten.COPPER: ((231, 124, 86), 1),
    fluids.Molten.EARTH: ((127, 54, 0), 2),
    fluids.Molten.GOLD: ((255, 255, 0), 1),
    fluids.Molten.IMPURITY: ((74, 47, 21), 2),
    fluids.Molten.IRON: ((200, 200, 200), 1),
    fluids.Molten.LEAD: ((163, 153, 229), 1),
    fluids.Molten.NICKEL: ((197, 197, 145), 1),
    fluids.Molten.PLATINUM: ((158, 235, 255), 1),
    fluids.Molten.SILVER: ((239, 248, 249), 1),
    fluids.Molten.TIN: ((233, 233, 233), 1),
}

TEXTURE_2_INDEX = {
    "textures/fluid/gray_lava_flow": 0,
    "textures/fluid/gray_molten_metal_still": 1,
    "textures/fluid/gray_lava_still": 2,
    "textures/fluid/basic_water_static": 3,
    "textures/fluid/gas": 4,
}
INDEX_2_TEXTUREURE = {v: k for k, v in TEXTURE_2_INDEX.items()}


NONCOLOR_TEXTURES = {
    "minecraft:water": "textures/fluid/water",
    "minecraft:flowing_water": "textures/fluid/flowing_water",
    "minecraft:lava": "textures/fluid/lava",
    "minecraft:flowing_lava": "textures/fluid/flowing_lava",
    #
    fluids.DeepLava.DEEPSLATE_LAVA: "textures/fluid/deepslate_lava_still",
    fluids.Common.METHANE_MUD: "textures/fluid/methane_mud",
}


def GetFluidTextureAndColor(fluid_id):
    # type: (str) -> tuple[str, tuple[int, int, int] | None]
    if fluid_id in NONCOLOR_TEXTURES:
        return NONCOLOR_TEXTURES.get(fluid_id, "textures/fluid/basic_fluid"), None
    elif fluid_id in FLUID_COLORS_AND_TEXTURES:
        color, texture_idx = FLUID_COLORS_AND_TEXTURES[fluid_id]
        return INDEX_2_TEXTUREURE[texture_idx], color
    else:
        return "textures/fluid/basic_fluid", None


def RegisterFluidTexture(fluid_id, texture_path, color=None):
    # type: (str, str, tuple[int, int, int] | None) -> None
    if color is None:
        NONCOLOR_TEXTURES[fluid_id] = texture_path
    else:
        idx = TEXTURE_2_INDEX.get(texture_path, None)
        if idx is None:
            idx = len(TEXTURE_2_INDEX)
            TEXTURE_2_INDEX[texture_path] = idx
            INDEX_2_TEXTUREURE[idx] = texture_path
        FLUID_COLORS_AND_TEXTURES[fluid_id] = (color, idx)
