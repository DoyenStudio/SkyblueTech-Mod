# codng=utf-8
from skybluetech_scripts.tooldelta.define import Item
from ..define import id_enum, tag_enum
from ..define.tag_enum import Wrench, Pincer
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe as MRecipe,
    Input,
)

recipes = RecipesCollection(
    id_enum.MACHINERY_WORKSTATION,
    # alloy furnace
    MRecipe(
        {
            0: Input("minecraft:copper_ingot"),
            1: Input(id_enum.HEAT_EXCHANGER),
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
    # assembler
    MRecipe(
        {
            0: Input("minecraft:lapis_lazuli"),
            1: Input("minecraft:paper"),
            2: Input("minecraft:lapis_lazuli"),
            3: Input(id_enum.Wrench.INVAR),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(id_enum.Pincer.INVAR),
            6: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            8: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.ASSEMBLER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        16,
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
        id_enum.ELECTRIC_HEATER,
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
            1: Input(tag_enum.StickTag.IRON, is_tag=True),
            3: Input("minecraft:iron_axe"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:iron_axe"),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.FORESTER,
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
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            1: Input(id_enum.REDSTONEFLUX_CORE),
            2: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            3: Input(id_enum.Wire.COPPER),
            4: Input(id_enum.HEAT_EXCHANGER),
            5: Input(id_enum.Wire.COPPER),
            6: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            7: Input("minecraft:hopper"),
            8: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
        },
        id_enum.GEO_THERMAL_GENERATOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # hover text displayer
    MRecipe(
        {
            1: Input("minecraft:glowstone_dust"),
            3: Input(tag_enum.StickTag.TIN, is_tag=True),
            4: Input(id_enum.SKYBLUE_CORE),
            5: Input(tag_enum.StickTag.TIN, is_tag=True),
            6: Input(id_enum.Plates.TIN),
            7: Input(id_enum.ControlCircuit.ADVANCED),
            8: Input(id_enum.Plates.TIN),
        },
        id_enum.HOVER_TEXT_DISPLAYER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        16,
    ),
    # hydroponic base
    MRecipe(
        {
            1: Input("minecraft:hopper"),
            3: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            4: Input("minecraft:chest"),
            5: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.HYDROPONIC_BASE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # hydroponic bed
    MRecipe(
        {
            0: Input("minecraft:glass_pane"),
            1: Input("minecraft:lantern"),
            2: Input("minecraft:glass_pane"),
            3: Input("minecraft:glass_pane"),
            5: Input("minecraft:glass_pane"),
            6: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input("minecraft:mud"),
            8: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.HYDROPONIC_BED,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # item splitter
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.TIN, is_tag=True),
            1: Input("minecraft:hopper"),
            2: Input(tag_enum.PlateTag.TIN, is_tag=True),
            3: Input(id_enum.Cable.STEEL),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(id_enum.Cable.STEEL),
            6: Input("minecraft:iron_ingot"),
            7: Input("minecraft:chest"),
            8: Input("minecraft:iron_ingot"),
        },
        id_enum.ITEM_SPLITTER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
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
    # magma centrifuge
    MRecipe(
        {
            1: Input(id_enum.ELECTRIC_MOTOR),
            3: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            6: Input("minecraft:iron_ingot"),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input("minecraft:iron_ingot"),
        },
        id_enum.MAGMA_CENTRIFUGE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # magma furnace
    MRecipe(
        {
            0: Input("minecraft:blaze_powder"),
            1: Input(id_enum.HEAT_PLATE),
            2: Input("minecraft:blaze_powder"),
            3: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            6: Input("minecraft:nether_brick"),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input("minecraft:nether_brick"),
        },
        id_enum.MAGMA_FURNACE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # metal press
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            1: Input("minecraft:piston"),
            2: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            3: Input("minecraft:heavy_weighted_pressure_plate"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:heavy_weighted_pressure_plate"),
            6: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.METAL_PRESS,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # mixer
    MRecipe(
        {
            1: Input(id_enum.ELECTRIC_MOTOR),
            3: Input(tag_enum.StickTag.TIN, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.StickTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.MIXER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # oil extractor
    MRecipe(
        {
            1: Input("minecraft:piston"),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.OIL_EXTRACTOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # pump
    MRecipe(
        {
            1: Input(id_enum.ELECTRIC_MOTOR),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.Tank.STEEL),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
        },
        id_enum.PUMP,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # redstone_furnace
    MRecipe(
        {
            1: Input("minecraft:furnace"),
            3: Input(id_enum.HEAT_PLATE),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.REDSTONE_FURNACE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # solar panel
    MRecipe(
        {
            1: Input("skybluetech:solar_panel_pane"),
            4: Input(tag_enum.StickTag.TIN, is_tag=True),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.SOLAR_PANEL,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # thermal generator
    MRecipe(
        {
            1: Input("minecraft:furnace"),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.REDSTONEFLUX_CORE),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input("minecraft:copper_ingot"),
        },
        id_enum.THERMAL_GENERATOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # wind generator
    MRecipe(
        {
            1: Input(tag_enum.StickTag.IRON, is_tag=True),
            3: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            4: Input(tag_enum.StickTag.IRON, is_tag=True),
            5: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.Wire.TIN),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.WIND_GENERATOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
)


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
