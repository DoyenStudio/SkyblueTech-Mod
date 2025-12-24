from ..define.id_enum.fluids import *
from ..mini_jei.machines.magma_centrifuge import *


recipes = [
    MagmaCentrifugeRecipe(
        DEEPSLATE_LAVA, 100,
        {
            1: Output(LIGHT_LAVA, 18),
            2: Output(MID_LAVA, 60),
            3: Output(HEAVY_LAVA, 18),
            4: Output(MOLTEN_EARTH, 4),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        LIGHT_LAVA, 100,
        {
            1: Output("minecraft:lava", 60),
            2: Output(MOLTEN_EARTH, 30),
            3: Output(MOLTEN_IMPURITY, 10),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        MID_LAVA, 100,
        {
            1: Output(MOLTEN_IRON, 40),
            2: Output(MOLTEN_COPPER, 20),
            1: Output(MOLTEN_TIN, 18),
            3: Output(MOLTEN_NICKEL, 15),
            4: Output(MOLTEN_IMPURITY, 7),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        HEAVY_LAVA, 100,
        {
            1: Output(MOLTEN_SILVER, 8),
            2: Output(MOLTEN_GOLD, 5),
            3: Output(MOLTEN_NICKEL, 50),
            4: Output(MOLTEN_IMPURITY, 20),
        },
        power_cost=80, tick_duration=20 * 5
    ),
]