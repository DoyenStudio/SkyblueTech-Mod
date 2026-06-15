# coding=utf-8
from .utils import SimpleEnum


class Acid(SimpleEnum):
    "酸性流体"

    SULFURIC_ACID = "skybluetech:sulfuric_acid"


class CommonGas(SimpleEnum):
    "对流体管道无特殊要求的气体"

    COMPRESSED_AIR = "skybluetech:compressed_air"
    HYDROGEN = "skybluetech:hydrogen"
    METHANE = "skybluetech:methane"


class CommonOil(SimpleEnum):
    "对流体管道无特殊要求的油类"

    RAW_OIL = "skybluetech:raw_oil"
    VEGETABLE_OIL = "skybluetech:vegetable_oil"
    LUBRICANT = "skybluetech:lubricant"


class Vanilla(SimpleEnum):
    "Minecraft 的流体"

    WATER = "minecraft:water"
    LAVA = "minecraft:lava"


class Common(CommonGas, CommonOil):
    "对流体管道无特殊要求的流体"

    WATER = Vanilla.WATER
    DISTILLED_WATER = "skybluetech:distilled_water"

    METHANE_MUD = "skybluetech:methane_mud"


class Gas(CommonGas):
    "气体"

    pass


class DeepLava(SimpleEnum):
    DEEPSLATE_LAVA = "skybluetech:deepslate_lava"
    HEAVY_LAVA = "skybluetech:heavy_lava"
    MID_LAVA = "skybluetech:mid_lava"
    LIGHT_LAVA = "skybluetech:light_lava"


class Molten(SimpleEnum):
    "熔融流体"

    EARTH = "skybluetech:molten_earth"
    IMPURITY = "skybluetech:molten_impurity"
    ROSIN = "skybluetech:molten_rosin"

    COPPER = "skybluetech:molten_copper"
    IRON = "skybluetech:molten_iron"
    GOLD = "skybluetech:molten_gold"
    TIN = "skybluetech:molten_tin"
    LEAD = "skybluetech:molten_lead"
    SILVER = "skybluetech:molten_silver"
    NICKEL = "skybluetech:molten_nickel"
    PLATINUM = "skybluetech:molten_platinum"


class HotFluid(Molten):
    "需要白铜流体管道运输的流体"

    LAVA = Vanilla.LAVA


class ExtremeHotFluid(HotFluid, DeepLava, Molten):
    "需要耐热流体管道运输的流体"

    pass


all_fluids = [
    Vanilla.WATER,
    Vanilla.LAVA,
    DeepLava.DEEPSLATE_LAVA,
    DeepLava.HEAVY_LAVA,
    DeepLava.MID_LAVA,
    DeepLava.LIGHT_LAVA,
    Common.COMPRESSED_AIR,
    Common.RAW_OIL,
    Common.LUBRICANT,
    Common.METHANE,
    Common.METHANE_MUD,
    Common.DISTILLED_WATER,
    Common.VEGETABLE_OIL,
    Molten.EARTH,
    Molten.IMPURITY,
    Molten.COPPER,
    Molten.IRON,
    Molten.GOLD,
    Molten.TIN,
    Molten.LEAD,
    Molten.SILVER,
    Molten.NICKEL,
    Molten.PLATINUM,
]
