# coding=utf-8
from .utils import SimpleEnum


class Batteries(SimpleEnum):
    JUNIOR = "skybluetech:battery_junior"
    LEADACID = "skybluetech:battery_leadacid"


class Coils(SimpleEnum):
    COPPER = "skybluetech:coil_copper"


class ControlCircuit(SimpleEnum):
    BASIC = "skybluetech:control_circuit_basic"
    ADVANCED = "skybluetech:control_circuit_advanced"
    PROFESSIONAL = "skybluetech:control_circuit_professional"


class Dusts(SimpleEnum):
    IRON = "skybluetech:iron_dust"
    GOLD = "skybluetech:gold_dust"
    COPPER = "skybluetech:copper_dust"

    ALUMITE = "skybluetech:alumite_dust"
    TIN = "skybluetech:tin_dust"
    LEAD = "skybluetech:lead_dust"
    LEAD_OXIDE = "skybluetech:lead_oxide_dust"
    LEAD_SULFATE = "skybluetech:lead_sulfate_dust"
    SILVER = "skybluetech:silver_dust"
    NICKEL = "skybluetech:nickel_dust"
    PLATINUM = "skybluetech:platinum_dust"
    TITANIUM = "skybluetech:titanium_dust"
    URANIUM = "skybluetech:uranium_dust"

    BRONZE = "skybluetech:bronze_dust"
    INVAR = "skybluetech:invar_dust"
    STEEL = "skybluetech:steel_dust"
    ALUMINUM = "skybluetech:aluminum_dust"
    CUPRONICKEL = "skybluetech:cupronickel_dust"

    ANCIENT_DEBRIS = "skybluetech:ancient_debris_dust"
    CARBON = "skybluetech:carbon_dust"
    CONCRETE = "skybluetech:concrete_dust"
    OBSIDIAN = "skybluetech:obsidian_dust"
    SULFUR = "skybluetech:sulfur_dust"


class FamicomCartidges(SimpleEnum):
    YELLOW = "skybluetech:famicom_cartidge_1"
    PURPLE = "skybluetech:famicom_cartidge_2"
    BLUE = "skybluetech:famicom_cartidge_3"


class Icons(SimpleEnum):
    SHEET = "skybluetech:sheet_item"


class Ingots(SimpleEnum):
    ALUMINUM = "skybluetech:aluminum_ingot"
    ALUMITE = "skybluetech:alumite_ingot"
    TIN = "skybluetech:tin_ingot"
    LEAD = "skybluetech:lead_ingot"
    SILVER = "skybluetech:silver_ingot"
    NICKEL = "skybluetech:nickel_ingot"
    PLATINUM = "skybluetech:platinum_ingot"
    TITANIUM = "skybluetech:titanium_ingot"

    BRONZE = "skybluetech:bronze_ingot"
    INVAR = "skybluetech:invar_ingot"
    STEEL = "skybluetech:steel_ingot"
    REFINED_IRON = "skybluetech:refined_iron_ingot"
    LIGHT_SKYBLUE = "skybluetech:light_skyblue_ingot"
    SOLDERING = "skybluetech:soldering_ingot"
    CUPRONICKEL = "skybluetech:cupronickel_ingot"
    ULTRAHEATINUM = "skybluetech:ultraheatinum_ingot"
    SUPERCONDUCT = "skybluetech:superconduct_ingot"


class MetalTools(SimpleEnum):
    BRONZE_AXE = "skybluetech:bronze_axe"
    BRONZE_PICKAXE = "skybluetech:bronze_pickaxe"
    BRONZE_SHOVEL = "skybluetech:bronze_shovel"
    BRONZE_HOE = "skybluetech:bronze_hoe"
    BRONZE_SWORD = "skybluetech:bronze_sword"
    BRONZE_MINING_HAMMER = "skybluetech:bronze_mining_hammer"

    INVAR_AXE = "skybluetech:invar_axe"
    INVAR_PICKAXE = "skybluetech:invar_pickaxe"
    INVAR_SHOVEL = "skybluetech:invar_shovel"
    INVAR_HOE = "skybluetech:invar_hoe"
    INVAR_SWORD = "skybluetech:invar_sword"
    INVAR_MINING_HAMMER = "skybluetech:invar_mining_hammer"


class ObjectUpgraders(SimpleEnum):
    ATTACK = "skybluetech:obj_upgrader_attack"
    AUTO_BURNING = "skybluetech:obj_upgrader_autoburning"
    DIGSPEED = "skybluetech:obj_upgrader_digspeed"
    ENERGY = "skybluetech:obj_upgrader_energy"
    FORTUNE = "skybluetech:obj_upgrader_fortune"
    PLATE_COMMON = "skybluetech:obj_upgrader_plate_common"
    PLATE_SPEC = "skybluetech:obj_upgrader_plate_spec"
    VEINMINER = "skybluetech:obj_upgrader_veinminer"
    SPEC_FARMING = "skybluetech:obj_upgrader_spec_farming"
    SPEC_NOFARM = "skybluetech:obj_upgrader_spec_nofarm"
    SPEC_NVISION = "skybluetech:obj_upgrader_spec_nvision"


class Paddle(SimpleEnum):
    IRON = "skybluetech:paddle_iron"
    STEEL = "skybluetech:paddle_steel"


class Pincer(SimpleEnum):
    # 新增物品后需在 machinery_workstation 中同步添加
    IRON = "skybluetech:pincer_iron"
    INVAR = "skybluetech:pincer_invar"


class Plates(SimpleEnum):
    IRON = "skybluetech:iron_plate"
    GOLD = "skybluetech:gold_plate"
    COPPER = "skybluetech:copper_plate"

    TIN = "skybluetech:tin_plate"
    LEAD = "skybluetech:lead_plate"
    SILVER = "skybluetech:silver_plate"
    NICKEL = "skybluetech:nickel_plate"
    PLATINUM = "skybluetech:platinum_plate"

    BRONZE = "skybluetech:bronze_plate"
    INVAR = "skybluetech:invar_plate"
    STEEL = "skybluetech:steel_plate"
    ALUMITE = "skybluetech:alumite_plate"
    CUPRONICKEL = "skybluetech:cupronickel_plate"
    ULTRAHEATINUM = "skybluetech:ultraheatinum_plate"
    SUPERCONDUCT = "skybluetech:superconduct_plate"


class RawOres(SimpleEnum):
    ALUMINUM = "skybluetech:raw_aluminum"
    TIN = "skybluetech:raw_tin"
    LEAD = "skybluetech:raw_lead"
    SILVER = "skybluetech:raw_silver"
    NICKEL = "skybluetech:raw_nickel"
    PLATINUM = "skybluetech:raw_platinum"
    TITANIUM = "skybluetech:raw_titanium"
    URANIUM = "skybluetech:raw_uranium"


class SkyblueTools(SimpleEnum):
    AXE = "skybluetech:skyblue_axe"
    PICKAXE = "skybluetech:skyblue_pickaxe"
    SHOVEL = "skybluetech:skyblue_shovel"
    HOE = "skybluetech:skyblue_hoe"
    SWORD = "skybluetech:skyblue_sword"


class Sticks(SimpleEnum):
    COPPER = "skybluetech:copper_stick"
    IRON = "skybluetech:iron_stick"
    TIN = "skybluetech:tin_stick"
    SILVER = "skybluetech:silver_stick"
    PLATINUM = "skybluetech:platinum_stick"
    STEEL = "skybluetech:steel_stick"
    BRONZE = "skybluetech:bronze_stick"
    INVAR = "skybluetech:invar_stick"
    CUPRONICKEL = "skybluetech:cupronickel_stick"
    SUPERCONDUCT = "skybluetech:superconduct_stick"


class Upgraders(SimpleEnum):
    EMPTY = "skybluetech:upgrader_plate_empty"
    BASIC_SPEED_UPGRADER = "skybluetech:upgrader_basic_speed"
    BASIC_ENERGY_UPGRADER = "skybluetech:upgrader_basic_energy"
    GENERIC_EXPANSION_UPGRADER = "skybluetech:upgrader_generic_expansion"
    GENERIC_AUTOSTOP = "skybluetech:upgrader_generic_autostop"
    GENERIC_FILTER_DEFAULT = "skybluetech:upgrader_generic_split"
    SPEC_MAGMA_FACTORY = "skybluetech:upgrader_spec_magma_factory"


class Wrench(SimpleEnum):
    # 新增物品后需在 machinery_workstation 中同步添加
    IRON = "skybluetech:wrench_iron"
    INVAR = "skybluetech:wrench_invar"


AIR_COMPRESS_UNIT = "skybluetech:air_compress_unit"
CIRCUIT_BASE_PLATE = "skybluetech:circuit_base_plate"
CRAFTING_TEMPLATE = "skybluetech:crafting_template"
DEACTIVATION_REDSTONE = "skybluetech:deactivation_redstone"
DRILL_TOP_STEEL = "skybluetech:drill_top_steel"
DRILL_TOP_ULTRAHEATINUM = "skybluetech:drill_top_ultraheatinum"
ELECTRIC_MOTOR = "skybluetech:electric_motor"
GLASS_TUBE = "skybluetech:glass_tube"
HEAT_EXCHANGER = "skybluetech:heat_exchanger"
HEAT_PLATE = "skybluetech:heat_plate"
INSCRIBING_TEMPLATE = "skybluetech:inscribing_template"
METAL_HAMMER = "skybluetech:metal_hammer"
REDSTONEFLUX_CORE = "skybluetech:redstoneflux_core"
RESIN = "skybluetech:resin"
RESIN_SPOON = "skybluetech:resin_spoon"
ROUGH_RUBBER = "skybluetech:rough_rubber"
ROSIN = "skybluetech:rosin"
SKYBLUE_CORE = "skybluetech:skyblue_core"
SULFUR = "skybluetech:sulfur"
SUNFLOWER_SEEDS = "skybluetech:sunflower_seeds"
TRANSMITTER_WRENCH = "skybluetech:transmitter_wrench"
TRANSMITTER_SETTINGS_WRENCH = "skybluetech:transmitter_settings_wrench"

SKYBLUE_HELMET = "skybluetech:skyblue_helmet"
SKYBLUE_CHESTPLATE = "skybluetech:skyblue_chestplate"
SKYBLUE_LEGGINGS = "skybluetech:skyblue_leggings"
SKYBLUE_BOOTS = "skybluetech:skyblue_boots"

GUIDANCE = "skybluetech:guidance"
