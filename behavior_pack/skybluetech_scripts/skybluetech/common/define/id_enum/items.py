# coding=utf-8
from .utils import SimpleEnum


class Batteries(SimpleEnum):
    JUNIOR = "skybluetech:battery_junior"
    LEADACID = "skybluetech:battery_leadacid"


class Coils(SimpleEnum):
    COPPER = "skybluetech:coil_copper"
    LARGE_COPPER = "skybluetech:large_copper_coil"


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
    IRON_OXIDE = "skybluetech:iron_oxide_dust"
    ALUMINUM_OXIDE = "skybluetech:aluminum_oxide_dust"
    TITANIUM_OXIDE = "skybluetech:titanium_oxide_dust"
    PURIFIED_CASSITERITE = "skybluetech:purified_cassiterite_dust"
    CALCIUM_CHLORIDE = "skybluetech:calcium_chloride_dust"
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
    SAWDUST = "skybluetech:sawdust"
    SULFUR = "skybluetech:sulfur_dust"
    UNDEAD = "skybluetech:undead_dust"
    EVIL_UNDEAD = "skybluetech:evil_undead_dust"


class FineConcentrates(SimpleEnum):
    IRON = "skybluetech:fine_iron_conc"
    COPPER = "skybluetech:fine_copper_conc"
    GOLD = "skybluetech:fine_gold_conc"
    ALUMINUM = "skybluetech:fine_aluminum_conc"
    TIN = "skybluetech:fine_tin_conc"
    LEAD = "skybluetech:fine_lead_conc"
    SILVER = "skybluetech:fine_silver_conc"
    NICKEL = "skybluetech:fine_nickel_conc"
    PLATINUM = "skybluetech:fine_platinum_conc"
    TITANIUM = "skybluetech:fine_titanium_conc"


class FilterCakes(SimpleEnum):
    IRON = "skybluetech:iron_filter_cake"
    COPPER = "skybluetech:copper_filter_cake"
    GOLD = "skybluetech:gold_filter_cake"
    ALUMINUM = "skybluetech:aluminum_filter_cake"
    TIN = "skybluetech:tin_filter_cake"
    LEAD = "skybluetech:lead_filter_cake"
    SILVER = "skybluetech:silver_filter_cake"
    NICKEL = "skybluetech:nickel_filter_cake"
    PLATINUM = "skybluetech:platinum_filter_cake"
    TITANIUM = "skybluetech:titanium_filter_cake"

    IRON_HYDROXIDE = "skybluetech:iron_hydroxide_cake"
    SILVER_CHLORIDE = "skybluetech:silver_chloride_cake"
    ALUMINUM_HYDROXIDE = "skybluetech:aluminum_hydroxide_cake"
    HYDRATED_TITANIUM_OXIDE = "skybluetech:titanium_hydrate_cake"
    MAGNESIUM_HYDROXIDE = "skybluetech:magnesium_hydroxide_cake"


MAGNESIUM_PELLET = "skybluetech:magnesium_pellet"
TITANIUM_SPONGE = "skybluetech:titanium_sponge"


class FamicomCartidges(SimpleEnum):
    YELLOW = "skybluetech:famicom_cartidge_1"
    PURPLE = "skybluetech:famicom_cartidge_2"
    BLUE = "skybluetech:famicom_cartidge_3"
    RED = "skybluetech:famicom_cartidge_4"
    CYAN = "skybluetech:famicom_cartidge_5"
    TEAL = "skybluetech:famicom_cartidge_6"


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
    PALLADIUM = "skybluetech:palladium_ingot"
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


class InscriberPress(SimpleEnum):
    EMPTY = "skybluetech:inscriber_press_empty"
    STICK = "skybluetech:inscriber_press_stick"


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


class Mixtures(SimpleEnum):
    ALUMINUM_ELECTROLYSIS = "skybluetech:aluminum_electrolysis_mix"
    TITANIUM_CHLORINATION = "skybluetech:titanium_chlorination_mix"


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
    SKYBLUE = "skybluetech:pincer_skyblue"


class Plates(SimpleEnum):
    ALUMINUM = "skybluetech:aluminum_plate"
    IRON = "skybluetech:iron_plate"
    GOLD = "skybluetech:gold_plate"
    COPPER = "skybluetech:copper_plate"

    TIN = "skybluetech:tin_plate"
    SKYBLUE = "skybluetech:skyblue_plate"
    LEAD = "skybluetech:lead_plate"
    SILVER = "skybluetech:silver_plate"
    NICKEL = "skybluetech:nickel_plate"
    PLATINUM = "skybluetech:platinum_plate"
    TITANIUM = "skybluetech:titanium_plate"

    BRONZE = "skybluetech:bronze_plate"
    INVAR = "skybluetech:invar_plate"
    STEEL = "skybluetech:steel_plate"
    ALUMITE = "skybluetech:alumite_plate"
    CUPRONICKEL = "skybluetech:cupronickel_plate"
    ULTRAHEATINUM = "skybluetech:ultraheatinum_plate"
    SUPERCONDUCT = "skybluetech:superconduct_plate"
    HDPE = "skybluetech:hdpe_plate"


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


class SortedOres(SimpleEnum):
    IRON = "skybluetech:sorted_iron_ore"
    COPPER = "skybluetech:sorted_copper_ore"
    GOLD = "skybluetech:sorted_gold_ore"
    ALUMINUM = "skybluetech:sorted_aluminum_ore"
    TIN = "skybluetech:sorted_tin_ore"
    LEAD = "skybluetech:sorted_lead_ore"
    SILVER = "skybluetech:sorted_silver_ore"
    NICKEL = "skybluetech:sorted_nickel_ore"
    PLATINUM = "skybluetech:sorted_platinum_ore"
    TITANIUM = "skybluetech:sorted_titanium_ore"


class Sticks(SimpleEnum):
    COPPER = "skybluetech:copper_stick"
    IRON = "skybluetech:iron_stick"
    ALUMINUM = "skybluetech:aluminum_stick"
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
    GENERIC_AUTO_EJECTION = "skybluetech:upgrader_generic_auto_ejection"
    GENERIC_AUTOSTOP = "skybluetech:upgrader_generic_autostop"
    GENERIC_EXPANSION_UPGRADER = "skybluetech:upgrader_generic_expansion"
    GENERIC_SPLIT = "skybluetech:upgrader_generic_split"
    SPEC_MAGMA_FACTORY = "skybluetech:upgrader_spec_magma_factory"
    SPEC_NITROGEN_EXTRACTION = "skybluetech:upgrader_spec_nitrogen_ext"


class Wrench(SimpleEnum):
    # 新增物品后需在 machinery_workstation 中同步添加
    IRON = "skybluetech:wrench_iron"
    INVAR = "skybluetech:wrench_invar"
    SKYBLUE = "skybluetech:wrench_skyblue"


class Cutter(SimpleEnum):
    STEEL = "skybluetech:steel_cutter"


AIR_COMPRESS_UNIT = "skybluetech:air_compress_unit"
CIRCUIT_BASE_PLATE = "skybluetech:circuit_base_plate"
CRAFTING_TEMPLATE = "skybluetech:crafting_template"
CRUDE_SALT = "skybluetech:crude_salt"
DEACTIVATION_REDSTONE = "skybluetech:deactivation_redstone"
DEACTIVATION_REDSTONE_BLOCK = "skybluetech:deactivation_redstone_block"
DRILL_TOP_STEEL = "skybluetech:drill_top_steel"
DRILL_TOP_ULTRAHEATINUM = "skybluetech:drill_top_ultraheatinum"
ELECTRIC_MOTOR = "skybluetech:electric_motor"
ELECTROLYTIC_PANE = "skybluetech:electrolytic_pane"
FAN_BLADE = "skybluetech:fan_blade"
GLASS_TUBE = "skybluetech:glass_tube"
HDPE_NUGGET = "skybluetech:hdpe_nugget"
HEAT_EXCHANGER = "skybluetech:heat_exchanger"
HEAT_PLATE = "skybluetech:heat_plate"
INSCRIBING_TEMPLATE = "skybluetech:inscribing_template"
LASER_PROBE = "skybluetech:laser_probe"
MACHINERY_BASE_LIGHT = "skybluetech:machinery_base_light"
METAL_HAMMER = "skybluetech:metal_hammer"
MINERAL_ASH = "skybluetech:mineral_ash"
MULTIBLOCK_STRUCTURE_SCEPTER = "skybluetech:multiblock_structure_scepter"
PLATINUM_CATALYST_MESH = "skybluetech:platinum_catalyst_mesh"
POLISHED_DIAMOND = "skybluetech:polished_diamond"
RAW_PAPER = "skybluetech:raw_paper"
REDSTONEFLUX_CORE = "skybluetech:redstoneflux_core"
RESIN = "skybluetech:resin"
RESIN_SPOON = "skybluetech:resin_spoon"
ROUGH_RUBBER = "skybluetech:rough_rubber"
ROSIN = "skybluetech:rosin"
SALT = "skybluetech:salt"
SEMI_COKE = "skybluetech:semi_coke"
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
