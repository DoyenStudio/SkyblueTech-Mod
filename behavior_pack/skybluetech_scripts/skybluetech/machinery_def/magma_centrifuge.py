from ..define.id_enum.fluids import *
from ..mini_jei.machines.magma_centrifuge import *


recipes = [
    MagmaCentrifugeRecipe(
        DEEPSLATE_LAVA,
        100,
        {
            1: Output(LIGHT_LAVA, 18),
            2: Output(MID_LAVA, 60),
            3: Output(HEAVY_LAVA, 18),
            4: Output(Molten.EARTH, 4),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        LIGHT_LAVA,
        100,
        {
            1: Output("minecraft:lava", 60),
            2: Output(Molten.EARTH, 30),
            3: Output(Molten.IMPURITY, 10),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        MID_LAVA,
        100,
        {
            1: Output(Molten.IRON, 40),
            2: Output(Molten.COPPER, 20),
            3: Output(Molten.TIN, 18),
            4: Output(Molten.NICKEL, 15),
            5: Output(Molten.IMPURITY, 7),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
    MagmaCentrifugeRecipe(
        HEAVY_LAVA,
        100,
        {
            1: Output(Molten.SILVER, 8),
            2: Output(Molten.GOLD, 5),
            3: Output(Molten.NICKEL, 50),
            4: Output(Molten.IRON, 65),
            5: Output(Molten.IMPURITY, 20),
        },
        power_cost=80,
        tick_duration=20 * 5,
    ),
]  # type: list[MachineRecipe]
