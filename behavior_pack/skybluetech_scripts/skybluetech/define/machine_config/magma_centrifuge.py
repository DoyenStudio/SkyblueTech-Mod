# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:magma_centrifuge"


class MagmaCentrifugeRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.magma_centrifuge_recipes"

    def __init__(self, input_fluid, input_volume, outputs, power_cost, tick_duration):
        # type: (str, float, dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: outputs},
            power_cost,
            tick_duration,
        )



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