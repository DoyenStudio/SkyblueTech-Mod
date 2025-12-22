# coding=utf-8
#
from ...mini_jei.machines.magma_centrifuge import *


recipes = [
    MagmaCentrifugeRecipe(
        "skybluetech:deepslate_lava", 100,
        {
            1: Output("skybluetech:light_lava", 18),
            2: Output("skybluetech:mid_lava", 60),
            3: Output("skybluetech:heavy_lava", 18),
            4: Output("skybluetech:molten_earth", 4),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        "skybluetech:light_lava", 100,
        {
            1: Output("minecraft:lava", 60),
            2: Output("skybluetech:molten_earth", 30),
            3: Output("skybluetech:molten_impurity", 10),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        "skybluetech:mid_lava", 100,
        {
            1: Output("skybluetech:molten_iron", 40),
            2: Output("skybluetech:molten_copper", 20),
            1: Output("skybluetech:molten_tin", 18),
            3: Output("skybluetech:molten_nickel", 15),
            4: Output("skybluetech:molten_impurity", 7),
        },
        power_cost=80, tick_duration=20 * 5
    ),
    MagmaCentrifugeRecipe(
        "skybluetech:heavy_lava", 100,
        {
            1: Output("skybluetech:molten_silver", 8),
            2: Output("skybluetech:molten_gold", 5),
            3: Output("skybluetech:molten_nickel", 50),
            4: Output("skybluetech:molten_impurity", 20),
        },
        power_cost=80, tick_duration=20 * 5
    ),
]