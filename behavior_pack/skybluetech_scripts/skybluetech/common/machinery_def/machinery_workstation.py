# codng=utf-8
from skybluetech_scripts.tooldelta.define import Item
from ...common.define import id_enum, tag_enum
from ...common.define.tag_enum import Wrench, Pincer
from ..mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe as MRecipe,
    Input,
)

recipes = [
    # alloy furnace
    MRecipe(
        {
            2: Input("minecraft:copper_ingot"),
            3: Input("minecraft:nether_brick"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:nether_brick"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.ALLOY_FURNACE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # charger
    MRecipe(
        {
            0: Input(tag_enum.StickTag.TIN, is_tag=True),
            1: Input(tag_enum.PlateTag.TIN, is_tag=True),
            3: Input(id_enum.Wire.COPPER),
            4: Input(id_enum.REDSTONEFLUX_CORE),
            6: Input(tag_enum.StickTag.TIN, is_tag=True),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.CHARGER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # compressor
    MRecipe(
        {
            1: Input("minecraft:piston"),
            3: Input(tag_enum.PlateTag.IRON, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.IRON, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.COMPRESSOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # digger
    MRecipe(
        {1: }),
    # macerator
    MRecipe(
        {
            1: Input(id_enum.ELECTRIC_MOTOR),
            3: Input("minecraft:flint"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:flint"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.MACERATOR,
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
