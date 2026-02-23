# codng=utf-8
from skybluetech_scripts.tooldelta.define import Item
from ..define.id_enum.machinery import MACERATOR
from ..define.tag_enum import Wrench, Pincer
from ..mini_jei.machines.machinery_workstation import (
    MachineryWorkstationRecipe as MRecipe,
    Input,
)

recipes = [
    MRecipe(
        {
            3: Input("minecraft:flint"),
            4: Input("skybluetech:machinery_frame"),
            5: Input("minecraft:flint"),
        },
        MACERATOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
]  # type: list[MRecipe]


def get_wrench_level(wrench_item):
    # type: (Item) -> int
    tags = wrench_item.GetBasicInfo().tags
    if Wrench.INVAR in tags:
        return MRecipe.LEVEL_INVAR
    elif Wrench.IRON in tags:
        return MRecipe.LEVEL_IRON
    return 0


def get_pincer_level(pincer_item):
    # type: (Item) -> int
    tags = pincer_item.GetBasicInfo().tags
    if Pincer.INVAR in tags:
        return MRecipe.LEVEL_INVAR
    elif Pincer.IRON in tags:
        return MRecipe.LEVEL_IRON
    return 0
