from ..id_enum import fluids

ROOT_TEXTURE = "textures/fluid"
TEXTURE_BASIC_FLUID = "textures/fluid/basic_fluid"
TEXTURE_WATER = "textures/fluid/water"
TEXTURE_LAVA = "textures/fluid/lava"

COLORS = {
    fluids.HEAVY_LAVA: ((168, 36, 36), 0),
    fluids.LIGHT_LAVA: ((255, 60, 0), 0),
    fluids.MID_LAVA: ((255, 0, 0), 0),
    fluids.MOLTEN_COPPER: ((231, 124, 86), 1),
    fluids.MOLTEN_EARTH: ((127, 54, 0), 2),
    fluids.MOLTEN_GOLD: ((255, 255, 0), 1),
    fluids.MOLTEN_IMPURITY: ((74, 47, 21), 2),
    fluids.MOLTEN_IRON: ((200, 200, 200), 1),
    fluids.MOLTEN_LEAD: ((163, 153, 229), 1),
    fluids.MOLTEN_NICKEL: ((197, 197, 145), 1),
    fluids.MOLTEN_PLATINUM: ((158, 235, 255), 1),
    fluids.MOLTEN_SILVER: ((239, 248, 249), 1),
    fluids.MOLTEN_TIN: ((233, 233, 233), 1),
    fluids.RAW_OIL: ((44, 39, 28), 3),
    fluids.METHANE: ((255, 240, 200), 4),
    fluids.LUBRICANT: ((255, 207, 0), 3),
}

IDX_MAP = {
    v: k for k, v in
    {   
        "gray_lava_flow": 0,
        "gray_molten_metal_still": 1,
        "gray_lava_still": 2,
        "basic_water_static": 3,
        "gas": 4,
    }.items()
}

BASIC_TEXTURES = {
    "minecraft:water": TEXTURE_WATER,
    "minecraft:flowing_water": TEXTURE_WATER,
    "minecraft:lava": TEXTURE_LAVA,
    "minecraft:flowing_lava": TEXTURE_LAVA,
    fluids.RAW_OIL: TEXTURE_BASIC_FLUID,
    #
    fluids.DEEPSLATE_LAVA: ROOT_TEXTURE + "/deepslate_lava_still",
    fluids.METHANE_MUD: ROOT_TEXTURE + "/methane_mud"
}

TYPE_BASIC_IMG = 0
TYPE_SPECIAL_IMG = 1
TYPE_ERROR = 2

def getBaseTexture(fluid_id):
    # type: (str) -> tuple[str, tuple[int, int, int] | None]
    if fluid_id in BASIC_TEXTURES:
        return BASIC_TEXTURES.get(fluid_id, TEXTURE_BASIC_FLUID), None
    elif fluid_id in COLORS:
        color, texture_idx = COLORS[fluid_id]
        return "textures/fluid/" + IDX_MAP[texture_idx], color
    else:
        return TEXTURE_BASIC_FLUID, None
