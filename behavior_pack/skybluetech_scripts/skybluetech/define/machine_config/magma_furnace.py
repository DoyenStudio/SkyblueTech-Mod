# coding=utf-8
#
from .define import MachineRecipe, Input, Output

def sec(second):
    # type: (float) -> int
    return int(second * 20)

raw2gold_vol = 432


recipes = [
    # lava
    MachineRecipe(
        {"item": {0: Input("minecraft:magma")}},
        {"fluid": {0: Output("minecraft:lava", 1000)}},
        power_cost=40, tick_duration=sec(5)
    ),
    MachineRecipe(
        {"item": {0: Input("minecraft:cobblestone")}},
        {"fluid": {0: Output("minecraft:lava", 250)}},
        power_cost=160, tick_duration=sec(20)
    ),
    MachineRecipe(
        {"item": {0: Input("minecraft:obsidian")}},
        {"fluid": {0: Output("minecraft:lava", 1000)}},
        power_cost=160, tick_duration=sec(14)
    ),
    MachineRecipe(
        {"item": {0: Input("minecraft:netherrack")}},
        {"fluid": {0: Output("minecraft:lava", 250)}},
        power_cost=75, tick_duration=sec(8)
    ),
    # mineral
    MachineRecipe(
        {"item": {0: Input("minecraft:raw_iron")}},
        {"fluid": {0: Output("skybluetech:molten_iron", raw2gold_vol)}},
        power_cost=50, tick_duration=sec(8)
    ),
    MachineRecipe(
        {"item": {0: Input("minecraft:raw_gold")}},
        {"fluid": {0: Output("skybluetech:molten_gold", raw2gold_vol)}},
        power_cost=40, tick_duration=sec(4.5)
    ),
    MachineRecipe(
        {"item": {0: Input("minecraft:raw_copper")}},
        {"fluid": {0: Output("skybluetech:molten_copper", raw2gold_vol)}},
        power_cost=50, tick_duration=sec(5)
    ),
    MachineRecipe(
        {"item": {0: Input("skybluetech:raw_tin")}},
        {"fluid": {0: Output("skybluetech:molten_tin", raw2gold_vol)}},
        power_cost=60, tick_duration=sec(5.5)
    ),
    MachineRecipe(
        {"item": {0: Input("skybluetech:raw_lead")}},
        {"fluid": {0: Output("skybluetech:molten_lead", raw2gold_vol)}},
        power_cost=70, tick_duration=sec(6)
    ),
    MachineRecipe(
        {"item": {0: Input("skybluetech:raw_nickel")}},
        {"fluid": {0: Output("skybluetech:molten_nickel", raw2gold_vol)}},
        power_cost=65, tick_duration=sec(5.5)
    ),
    MachineRecipe(
        {"item": {0: Input("skybluetech:raw_silver")}},
        {"fluid": {0: Output("skybluetech:molten_silver", raw2gold_vol)}},
        power_cost=45, tick_duration=sec(4.5)
    ),
    MachineRecipe(
        {"item": {0: Input("skybluetech:raw_platinum")}},
        {"fluid": {0: Output("skybluetech:molten_platinum", raw2gold_vol)}},
        power_cost=45, tick_duration=sec(4.5)
    ),
]