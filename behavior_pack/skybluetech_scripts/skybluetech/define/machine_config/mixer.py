# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:mixer"
TAG_DUST_BLOCK = "dust_block"


class MixerRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.mixer_recipes"

    def __init__(
        self,
        input_fluid, # type: str
        input_volume, # type: float
        input_item, # type: str
        input_count, # type: int
        output_item, # type: str
        output_count, # type: int
        power_cost, # type: int
        tick_duration, # type: int
    ):
        MachineRecipe.__init__(
            self,
            {
                CategoryType.FLUID: {0: Input(input_fluid, input_volume)},
                CategoryType.ITEM: {0: Input(input_item, input_count)},
            },
            {CategoryType.ITEM: {1: Output(output_item, output_count)}},
            power_cost,
            tick_duration,
        )


recipes = [
    MixerRecipe(
        "minecraft:lava", 500,
        "minecraft:netherrack", 1,
        "minecraft:magma", 1,
        tick_duration=80,
        power_cost=40,
    ),
    MixerRecipe(
        "minecraft:water", 400,
        "skybluetech:dust_block", 1,
        "minecraft:clay", 1,
        tick_duration=40,
        power_cost=30,
    ),
]
