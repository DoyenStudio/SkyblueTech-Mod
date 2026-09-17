# coding=utf-8
from ...common.define import id_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.misc.industrial_researching import IndustrialResearchingRecipe, Input

all_researchings = RecipesCollection(
    "IndustrialResearching",
    IndustrialResearchingRecipe(
        [
            Input("minecraft:redstone", 192),
            Input("minecraft:quartz", 72),
            Input("minecraft:lapis_lazuli", 40),
            Input(id_enum.Coils.COPPER, 32),
            Input(id_enum.ControlCircuit.ADVANCED, 24),
            Input(id_enum.Wire.COPPER, 12),
            Input(id_enum.SKYBLUE_CORE, 4),
        ],
        40,
        id_enum.Upgraders.BASIC_SPEED_UPGRADER,
    ),
    IndustrialResearchingRecipe(
        [
            Input(id_enum.DEACTIVATION_REDSTONE, 48),
            Input(id_enum.Wire.COPPER_INSULATED, 32),
            Input(id_enum.REDSTONEFLUX_CORE, 12),
            Input("minecraft:amethyst_shard", 9),
            Input(id_enum.ControlCircuit.ADVANCED, 4),
            Input(id_enum.HEAT_EXCHANGER, 2),
        ],
        24,
        id_enum.Upgraders.BASIC_ENERGY_UPGRADER,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:string", 32),
            Input(id_enum.Sticks.INVAR, 16),
            Input("minecraft:redstone", 4),
        ],
        15,
        id_enum.Upgraders.GENERIC_SPLIT,
    ),
    IndustrialResearchingRecipe(
        [
            Input(id_enum.Coils.COPPER, 24),
            Input(id_enum.Sticks.COPPER, 20),
            Input("minecraft:redstone", 16),
            Input("minecraft:red_nether_brick", 10),
            Input("minecraft:magma", 8),
        ],
        12,
        id_enum.Upgraders.SPEC_MAGMA_FACTORY,
    ),
    IndustrialResearchingRecipe(
        [
            Input(id_enum.Sticks.STEEL, 32),
            Input(id_enum.Sticks.BRONZE, 28),
            Input("minecraft:redstone", 24),
            Input("minecraft:sticky_piston", 16),
            Input("minecraft:scaffolding", 10),
        ],
        24,
        id_enum.Upgraders.GENERIC_EXPANSION_UPGRADER,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:redstone", 32),
            Input("minecraft:phantom_membrane", 8),
            Input(id_enum.Sticks.STEEL, 24),
            Input(id_enum.Sticks.PLATINUM, 2),
            Input(id_enum.Sticks.COPPER, 2),
            Input(id_enum.ControlCircuit.BASIC, 2),
        ],
        0,
        id_enum.Upgraders.SPEC_NITROGEN_EXTRACTION,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:quartz", 45),
            Input("minecraft:prismarine_shard", 16),
            Input(id_enum.Plates.INVAR, 8),
        ],
        24,
        id_enum.ObjectUpgraders.ATTACK,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:redstone", 48),
            Input("minecraft:amethyst_shard", 32),
            Input(id_enum.ELECTRIC_MOTOR, 4),
        ],
        24,
        id_enum.ObjectUpgraders.DIGSPEED,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:furnace", 18),
            Input("skybluetech:deactivation_redstone", 16),
            Input(id_enum.HEAT_PLATE, 12),
        ],
        16,
        id_enum.ObjectUpgraders.AUTO_BURNING,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:lapis_block", 20),
            Input(id_enum.Plates.PLATINUM, 16),
            Input(id_enum.Plates.SILVER, 16),
            Input(id_enum.Sticks.SILVER, 16),
            Input(id_enum.ControlCircuit.ADVANCED, 4),
        ],
        30,
        id_enum.ObjectUpgraders.FORTUNE,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:sticky_piston", 14),
            Input("minecraft:iron_pickaxe", 12),
            Input(id_enum.ELECTRIC_MOTOR, 8),
            Input(id_enum.DRILL_TOP_STEEL, 4),
        ],
        8,
        id_enum.ObjectUpgraders.VEINMINER,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:piston", 14),
            Input("minecraft:iron_hoe", 8),
            Input("minecraft:hay_block", 6),
            Input(id_enum.ELECTRIC_MOTOR, 5),
        ],
        8,
        id_enum.ObjectUpgraders.SPEC_FARMING,
    ),
    IndustrialResearchingRecipe(
        [
            Input("minecraft:redstone", 96),
            Input(id_enum.DEACTIVATION_REDSTONE, 64),
            Input(id_enum.Coils.COPPER, 16),
            Input(id_enum.ControlCircuit.BASIC, 4),
        ],
        32,
        id_enum.ObjectUpgraders.ENERGY,
    ),
)
