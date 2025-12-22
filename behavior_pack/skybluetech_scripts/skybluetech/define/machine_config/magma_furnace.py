# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

def sec(second):
    # type: (float) -> int
    return int(second * 20)

MACHINE_ID = "skybluetech:magma_furnace"
raw2gold_vol = 432


class MagmaFurnaceRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.magma_furnace_recipes"

    def __init__(self, input_id, is_tag, output_fluid, output_volume, power_cost, tick_duration):
        # type: (str, bool, str, float, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_id, is_tag=is_tag)}},
            {CategoryType.FLUID: {0: Output(output_fluid, output_volume)}},
            power_cost,
            tick_duration,
        )


recipes = [
    # lava
    MagmaFurnaceRecipe(
        "minecraft:magma", False,
        "minecraft:lava", 1000,
        power_cost=40, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:cobblestone", False,
        "minecraft:lava", 250,
        power_cost=160, tick_duration=sec(20)
    ),
    MagmaFurnaceRecipe(
        "minecraft:obsidian", False,
        "minecraft:lava", 1000,
        power_cost=160, tick_duration=sec(14)
    ),
    MagmaFurnaceRecipe(
        "minecraft:netherrack", False,
        "minecraft:lava", 250,
        power_cost=75, tick_duration=sec(8)
    ),
    # mineral
    MagmaFurnaceRecipe(
        "minecraft:raw_iron", False,
        "skybluetech:molten_iron", raw2gold_vol,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_gold", False,
        "skybluetech:molten_gold", raw2gold_vol,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_copper", False,
        "skybluetech:molten_copper", raw2gold_vol,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        "raws/tin", True,
        "skybluetech:molten_tin", raw2gold_vol,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "raws/lead", True,
        "skybluetech:molten_lead", raw2gold_vol,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        "raws/nickel", True,
        "skybluetech:molten_nickel", raw2gold_vol,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "raws/silver", True,
        "skybluetech:molten_silver", raw2gold_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "raws/platinum", True,
        "skybluetech:molten_platinum", raw2gold_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
]