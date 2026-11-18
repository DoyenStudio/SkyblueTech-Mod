# coding=utf-8
from .utils import SimpleEnum

class Fluids(SimpleEnum):
    "所有流体"

    pass

class Acid(Fluids):
    "酸性流体"

    HYDROGEN_CHLORIDE = "skybluetech:hydrogen_chloride"
    SULFURIC_ACID = "skybluetech:sulfuric_acid"
    CONCENTRATED_SULFURIC_ACID = "skybluetech:concentrated_sulfuric_acid"
    SO3 = "skybluetech:so3"


class Alkali(Fluids):
    "碱性流体"

    SODIUM_HYDROXIDE_SOLUTION = "skybluetech:sodium_hydroxide_solution"


class Chemical(Fluids):
    "需要化学流体管道运输的化学品"

    ALKALI_LIQUOR = "skybluetech:alkali_liquor"
    ALUMINATE = "skybluetech:aluminate"
    BARREN_HCL = "skybluetech:barren_hcl"
    CALCIUM_LIQUOR = "skybluetech:calcium_liquor"
    COAL_TAR = "skybluetech:coal_tar"
    COPPER_LEACH = "skybluetech:copper_leach"
    COPPER_SOLUTION = "skybluetech:copper_solution"
    CRUDE_TICL4 = "skybluetech:crude_ticl4"
    FLOTATION_WASTE = "skybluetech:flotation_waste"
    GOLD_LEACH = "skybluetech:gold_leach"
    GOLD_SOLUTION = "skybluetech:gold_solution"
    HYDROCHLORIC_ACID = "skybluetech:hydrochloric_acid"
    IRON_LEACH = "skybluetech:iron_leach"
    MGCL2_SOLUTION = "skybluetech:mgcl2_solution"
    MINERAL_COLLECTOR = "skybluetech:mineral_collector"
    MOLTEN_MGCL2 = "skybluetech:molten_mgcl2"
    NICKEL_LEACH = "skybluetech:nickel_leach"
    NICKEL_SOLUTION = "skybluetech:nickel_solution"
    PEROXIDE = "skybluetech:peroxide"
    PLATINUM_LEACH = "skybluetech:platinum_leach"
    PLATINUM_SOLUTION = "skybluetech:platinum_solution"
    PURE_TICL4 = "skybluetech:pure_ticl4"
    RAW_SEAWATER = "skybluetech:raw_seawater"
    SILVER_SLURRY = "skybluetech:silver_slurry"
    TIN_ACID_WASTE = "skybluetech:tin_acid_waste"
    TIN_DEACID_WASTE = "skybluetech:tin_deacid_waste"
    TIN_NEUTRAL_LIQ = "skybluetech:tin_neutral_liq"
    TITANIUM_ACID = "skybluetech:titanium_acid"
    TITANYL_LEACH = "skybluetech:titanyl_leach"
    WOOD_CREOSOTE = "skybluetech:wood_creosote"


class Gas(Fluids):
    "气体"

    pass


class ChemicalGas(Chemical, Gas):
    "需要化学流体管道运输的气体"

    ACID_VAPOR = "skybluetech:acid_vapor"
    CARBON_DIOXIDE = "skybluetech:carbon_dioxide"
    SULFUR_DIOXIDE = "skybluetech:sulfur_dioxide"


class Oil(Fluids):
    "油类"

    pass


class Vanilla(Fluids):
    "Minecraft 的流体"

    WATER = "minecraft:water"
    LAVA = "minecraft:lava"


class Common(Fluids):
    "对流体管道无特殊要求的流体"

    pass


class CommonGas(Common, Gas):
    "对流体管道无特殊要求的气体"

    ARGON = "skybluetech:argon"
    CHLORINE = "skybluetech:chlorine"
    COMPRESSED_AIR = "skybluetech:compressed_air"
    ETHYLENE = "skybluetech:ethylene"
    HYDROGEN = "skybluetech:hydrogen"
    NITROGEN = "skybluetech:nitrogen"
    METHANE = "skybluetech:methane"
    OXYGEN = "skybluetech:oxygen"
    PURE_METHANE = "skybluetech:pure_methane"
    WATER_VAPOR = "skybluetech:water_vapor"


class CommonOil(Common, Oil):
    "对流体管道无特殊要求的油类"

    FUEL_OIL = "skybluetech:fuel_oil"
    RAW_OIL = "skybluetech:raw_oil"
    TREE_OIL = "skybluetech:tree_oil"
    VEGETABLE_OIL = "skybluetech:vegetable_oil"
    LUBRICANT = "skybluetech:lubricant"


class CommonLiquid(Common):
    "对流体管道无特殊要求的液体"

    BRINE = "skybluetech:brine"
    CALCIUM_CHLORIDE = "skybluetech:calcium_chloride"
    CONCRETE_ACCEL = "skybluetech:concrete_accel"
    DILUTE_BRINE = "skybluetech:dilute_brine"
    EVIL_UNDEAD = "skybluetech:evil_undead"
    LIQUID_AIR = "skybluetech:liquid_air"
    LIQUID_RESIN = "skybluetech:liquid_resin"
    ORGANIC_WASTE = "skybluetech:organic_waste"
    PROCESS_WATER = "skybluetech:process_water"
    SATURATED_BRINE = "skybluetech:saturated_brine"
    WATER = Vanilla.WATER
    DISTILLED_WATER = "skybluetech:distilled_water"
    METHANE_MUD = "skybluetech:methane_mud"


class HotFluid(Fluids):
    "需要白铜流体管道运输的流体"

    pass
    MOLTEN_POLYETHYLENE = "skybluetech:molten_polyethylene"


class ExtremeHotFluid(Fluids):
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
    PALLADIUM = "skybluetech:molten_palladium"
    ROSIN = "skybluetech:molten_rosin"

    COPPER = "skybluetech:molten_copper"
    IRON = "skybluetech:molten_iron"
    GOLD = "skybluetech:molten_gold"
    TIN = "skybluetech:molten_tin"
    LEAD = "skybluetech:molten_lead"
    SILVER = "skybluetech:molten_silver"
    NICKEL = "skybluetech:molten_nickel"
    PLATINUM = "skybluetech:molten_platinum"

