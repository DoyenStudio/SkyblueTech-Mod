# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:compressor"
DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80


class CompressorRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.compressor_recipes"

    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[int, Input], dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: inputs},
            {CategoryType.ITEM: outputs},
            power_cost,
            tick_duration,
        )

def gen_preset_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        output, # type: str
    ):
        return CompressorRecipe(
            {0: Input(input)}, {1: Output(output)}, power_cost, tick_duration
        )
    return generate_recipe

def gen_preset_tagged_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        output, # type: str
    ):
        return CompressorRecipe(
            {0: Input(input, is_tag=True)}, {1: Output(output)}, power_cost, tick_duration
        )
    return generate_recipe


preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_preset_tagged_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)

recipes = [
    # Minecraft
    # Ingot 2 Plate
    preset("minecraft:copper_ingot", "skybluetech:copper_plate"), 
    preset("minecraft:iron_ingot", "skybluetech:iron_plate"),
    preset("minecraft:gold_ingot", "skybluetech:gold_plate"),
    preset_tagged("ingots/tin", "skybluetech:tin_plate"),
    preset_tagged("ingots/lead", "skybluetech:lead_plate"),
    preset_tagged("ingots/silver", "skybluetech:silver_plate"),
    preset_tagged("ingots/platinum", "skybluetech:platinum_plate"),
    preset_tagged("ingots/nickel", "skybluetech:nickel_plate"),
]
