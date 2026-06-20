# coding=utf-8
from .utils import SimpleEnum


class Acid(SimpleEnum):
    "酸性流体"

    SULFURIC_ACID = "skybluetech:sulfuric_acid"
    CONCENTRATED_SULFURIC_ACID = "skybluetech:concentrated_sulfuric_acid"
    SO3 = "skybluetech:so3"


class Gas(SimpleEnum):
    "气体"

    pass


class Oil(SimpleEnum):
    "油类"

    pass


class Vanilla(SimpleEnum):
    "Minecraft 的流体"

    WATER = "minecraft:water"
    LAVA = "minecraft:lava"


class Common(SimpleEnum):
    "对流体管道无特殊要求的流体"

    pass


class CommonGas(Common, Gas):
    "对流体管道无特殊要求的气体"

    COMPRESSED_AIR = "skybluetech:compressed_air"
    HYDROGEN = "skybluetech:hydrogen"
    METHANE = "skybluetech:methane"
    WATER_VAPOR = "skybluetech:water_vapor"


class CommonOil(Common, Oil):
    "对流体管道无特殊要求的油类"

    RAW_OIL = "skybluetech:raw_oil"
    VEGETABLE_OIL = "skybluetech:vegetable_oil"
    LUBRICANT = "skybluetech:lubricant"


class CommonLiquid(Common):
    "对流体管道无特殊要求的液体"

    WATER = Vanilla.WATER
    DISTILLED_WATER = "skybluetech:distilled_water"
    METHANE_MUD = "skybluetech:methane_mud"


class HotFluid(SimpleEnum):
    "需要白铜流体管道运输的流体"

    pass


class ExtremeHotFluid(SimpleEnum):
    "需要耐热流体管道运输的流体"

    pass


class HotLava(HotFluid):
    "需要白铜流体管道运输的熔岩"

    LAVA = Vanilla.LAVA


class DeepLava(ExtremeHotFluid):
    DEEPSLATE_LAVA = "skybluetech:deepslate_lava"
    HEAVY_LAVA = "skybluetech:heavy_lava"
    MID_LAVA = "skybluetech:mid_lava"
    LIGHT_LAVA = "skybluetech:light_lava"


class Molten(HotFluid):
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


all_fluids = [
    CommonLiquid.WATER,
    Vanilla.LAVA,
    DeepLava.DEEPSLATE_LAVA,
    DeepLava.HEAVY_LAVA,
    DeepLava.MID_LAVA,
    DeepLava.LIGHT_LAVA,
    CommonGas.COMPRESSED_AIR,
    CommonOil.RAW_OIL,
    CommonOil.LUBRICANT,
    CommonGas.METHANE,
    CommonGas.WATER_VAPOR,
    CommonLiquid.METHANE_MUD,
    CommonLiquid.DISTILLED_WATER,
    CommonOil.VEGETABLE_OIL,
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
