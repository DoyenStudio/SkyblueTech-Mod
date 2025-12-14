ROOT_TEXTURE = "textures/fluid"
TEXTURE_BASIC_FLUID = "textures/fluid/basic_fluid"
TEXTURE_WATER = "textures/fluid/water"
TEXTURE_LAVA = "textures/fluid/lava"

COLORS = {
    "skybluetech:heavy_lava": ((168, 36, 36), 0),
    "skybluetech:light_lava": ((255, 60, 0), 0),
    "skybluetech:mid_lava": ((255, 0, 0), 0),
    "skybluetech:molten_copper": ((231, 124, 86), 1),
    "skybluetech:molten_earth": ((127, 54, 0), 2),
    "skybluetech:molten_gold": ((255, 255, 0), 1),
    "skybluetech:molten_impurity": ((74, 47, 21), 2),
    "skybluetech:molten_iron": ((200, 200, 200), 1),
    "skybluetech:molten_lead": ((163, 153, 229), 1),
    "skybluetech:molten_nickel": ((197, 197, 145), 1),
    "skybluetech:molten_platinum": ((158, 235, 255), 1),
    "skybluetech:molten_silver": ((239, 248, 249), 1),
    "skybluetech:molten_tin": ((233, 233, 233), 1),
    "skybluetech:raw_oil": ((44, 39, 28), 3),
    "skybluetech:methane": ((255, 240, 200), 4),
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
    "skybluetech:raw_oil": TEXTURE_BASIC_FLUID,
    #
    "skybluetech:deepslate_lava": ROOT_TEXTURE + "/deepslate_lava_still",
    "skybluetech:methane_mud": ROOT_TEXTURE + "/methane_mud"
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
