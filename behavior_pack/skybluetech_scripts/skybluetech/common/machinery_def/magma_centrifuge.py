from ..define.id_enum import (
    Machinery,
    fluids,
    Molten,
    DeepLava,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.magma_centrifuge import (
    MachineRecipe,
    MagmaCentrifugeRecipe,
    Output,
)

STORE_RF_MAX = 8800
FLUID_SLOT_MAX_VOLUMES = (2000, 500, 500, 500, 500, 500, 500)

recipes = RecipesCollection(
    Machinery.MAGMA_CENTRIFUGE,
    MagmaCentrifugeRecipe(
        DeepLava.DEEPSLATE_LAVA,
        100,
        {
            1: Output(DeepLava.LIGHT_LAVA, 18),
            2: Output(DeepLava.MID_LAVA, 60),
            3: Output(DeepLava.HEAVY_LAVA, 18),
            4: Output(Molten.EARTH, 4),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        DeepLava.LIGHT_LAVA,
        100,
        {
            1: Output(fluids.Vanilla.LAVA, 60),
            2: Output(Molten.EARTH, 30),
            3: Output(Molten.IMPURITY, 10),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        DeepLava.MID_LAVA,
        100,
        {
            1: Output(Molten.IRON, 40),
            2: Output(Molten.COPPER, 20),
            3: Output(Molten.TIN, 18),
            4: Output(Molten.IMPURITY, 7),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        DeepLava.HEAVY_LAVA,
        100,
        {
            1: Output(Molten.SILVER, 5),
            2: Output(Molten.GOLD, 2),
            3: Output(Molten.NICKEL, 50),
            4: Output(Molten.IMPURITY, 20),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
)  # type: RecipesCollection[MachineRecipe]
