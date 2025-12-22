# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:freezer"


class FreezerRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.freezer_recipes"

    def __init__(
        self,
        index, # type: int
        input_fluid, # type: str
        input_volume, # type: float
        output_item, # type: str
        output_count, # type: int
        power_cost, # type: int
        tick_duration, # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.ITEM: {0: Output(output_item, output_count)}},
            power_cost,
            tick_duration,
        )
        self.index = index


recipes = {
    0: FreezerRecipe(
        0, 
        "minecraft:water", 250,
        "minecraft:snowball", 1,
        tick_duration=20, power_cost=50
    ),
    1: FreezerRecipe(
        1,
        "minecraft:water", 1000,
        "minecraft:snow", 1,
        tick_duration=80, power_cost=40
    ),
    2: FreezerRecipe(
        2,
       "minecraft:water", 1000,
        "minecraft:ice", 1,
        tick_duration=80, power_cost=50
    ),
    3: FreezerRecipe(
        3,
        "minecraft:water", 1000,
        "minecraft:packed_ice", 1,
        tick_duration=75, power_cost=45
    ),
    4: FreezerRecipe(
        4,
        "minecraft:water", 10000,
        "minecraft:blue_ice", 1,
        tick_duration=400, power_cost=50
    ),
}
