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
        {
            1: Input(id_enum.DRILL_TOP),
            3: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            4: Input(id_enum.ELECTRIC_MOTOR),
            5: Input(id_enum.Plates.STEEL),
            6: Input(id_enum.Wire.COPPER),
            7: Input(id_enum.Cable.STEEL),
            8: Input(id_enum.Wire.COPPER),
        },
        id_enum.DIGGER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        12,
    ),
    # distillation chamber
    MRecipe(
        {
            1: Input("minecraft:glass"),
            4: Input(id_enum.MACHINERY_FRAME),
            7: Input(tag_enum.PlateTag.COPPER, is_tag=True),
        },
        id_enum.DISTILLATION_CHAMBER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # electric crafter
    MRecipe(
        {
            1: Input("minecraft:crafting_table"),
            3: Input("minecraft:piston"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:piston"),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.ADVANCED),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.ELECTRIC_CRAFTER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # electric heater
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.IRON, is_tag=True),
            1: Input(id_enum.HEAT_PLATE),
            2: Input(tag_enum.PlateTag.IRON, is_tag=True),
            3: Input(tag_enum.PlateTag.COPPER, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.COPPER, is_tag=True),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.FARMING_STATION,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # farming station
    MRecipe(
        {
            3: Input("minecraft:iron_hoe"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:iron_hoe"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.FARMING_STATION,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # fluid condenser
    MRecipe(
        {
            1: Input(id_enum.HEAT_EXCHANGER),
            3: Input("minecraft:blue_ice"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:blue_ice"),
            6: Input(id_enum.Pipe.BRONZE),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input(id_enum.Cable.STEEL),
        },
        id_enum.FLUID_CONDENSER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # forester
    MRecipe(
        {
            3: Input("minecraft:iron_axe"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:iron_axe"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.FARMING_STATION,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # freezer
    MRecipe(
        {
            1: Input(id_enum.AIR_COMPRESS_UNIT),
            3: Input("minecraft:blue_ice"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:blue_ice"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.FREEZER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # geo thermal generator
    # MRecipe({5: Input(id_enum.HEAT_EXCHANGER)}),
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
