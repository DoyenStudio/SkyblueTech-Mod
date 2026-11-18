# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    Chemical, CommonLiquid, FilterCakes, Machinery, RawOres, SortedOres,
)
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType, Input, Output,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.flotation_machine import (
    FlotationMachineRecipe,
)

STORE_RF_MAX = 32000
MAX_FLUID_VOLUME = 8000
FLUID_SLOT_MAX_VOLUMES = {0: MAX_FLUID_VOLUME, 1: MAX_FLUID_VOLUME, 2: MAX_FLUID_VOLUME}

_ORE_OUTPUTS = (
    ("minecraft:raw_iron", SortedOres.IRON, FilterCakes.IRON),
    ("minecraft:raw_copper", SortedOres.COPPER, FilterCakes.COPPER),
    ("minecraft:raw_gold", SortedOres.GOLD, FilterCakes.GOLD),
    (RawOres.ALUMINUM, SortedOres.ALUMINUM, FilterCakes.ALUMINUM),
    (RawOres.TIN, SortedOres.TIN, FilterCakes.TIN),
    (RawOres.LEAD, SortedOres.LEAD, FilterCakes.LEAD),
    (RawOres.SILVER, SortedOres.SILVER, FilterCakes.SILVER),
    (RawOres.NICKEL, SortedOres.NICKEL, FilterCakes.NICKEL),
    (RawOres.PLATINUM, SortedOres.PLATINUM, FilterCakes.PLATINUM),
    (RawOres.TITANIUM, SortedOres.TITANIUM, FilterCakes.TITANIUM),
)

recipes = RecipesCollection(Machinery.FLOTATION_MACHINE)  # type: RecipesCollection[FlotationMachineRecipe]

for raw_ore, sorted_ore, filter_cake in _ORE_OUTPUTS:
    recipes.add_recipe(FlotationMachineRecipe(
        inputs={
            CategoryType.ITEM: {0: Input(raw_ore, 1)},
            CategoryType.FLUID: {
                0: Input(Chemical.MINERAL_COLLECTOR, 200),
                1: Input(CommonLiquid.WATER, 200),
            },
        },
        outputs={
            CategoryType.ITEM: {1: Output(sorted_ore, 1), 2: Output(filter_cake, 1)},
            CategoryType.FLUID: {2: Output(Chemical.FLOTATION_WASTE, 300)},
        },
        power_cost=128,
        tick_duration=200,
    ))
