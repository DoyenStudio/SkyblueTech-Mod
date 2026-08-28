# codng=utf-8
from skybluetech_scripts.tooldelta.define import Item

from ..define import id_enum, tag_enum
from ..define.tag_enum import Pincer, Wrench
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.machinery_workstation import (
    Input,
)
from ..mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe as MRecipe,
)

K_CRAFTING_PROGRESS = "st:crafting_progress"
K_OUTPUT_ITEM_ID = "st:output_item_id"
K_NEED_TOOL = "st:need_tool"

recipes = RecipesCollection(
    id_enum.Machinery.MACHINERY_WORKSTATION,
    # air compressor
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.INVAR, is_tag=True),
            1: Input(id_enum.Pipe.BRONZE),
            2: Input(tag_enum.PlateTag.INVAR, is_tag=True),
            3: Input("minecraft:iron_bars"),
            4: Input(id_enum.AIR_COMPRESS_UNIT),
            5: Input("minecraft:iron_bars"),
            6: Input(tag_enum.PlateTag.INVAR, is_tag=True),
            7: Input(id_enum.Pipe.BRONZE),
            8: Input(tag_enum.PlateTag.INVAR, is_tag=True),
        },
        id_enum.Machinery.AIR_COMPRESSOR,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    # alloy furnace
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.COPPER, is_tag=True),
            1: Input("minecraft:blast_furnace"),
            2: Input(tag_enum.PlateTag.COPPER, is_tag=True),
            3: Input("minecraft:nether_brick"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:nether_brick"),
            6: Input("minecraft:redstone"),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input("minecraft:redstone"),
        },
        id_enum.Machinery.ALLOY_FURNACE,
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
        id_enum.Machinery.ASSEMBLER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        16,
    ),
    # battery matrix structure
    MRecipe(
        {
            1: Input(id_enum.REDSTONEFLUX_CORE),
            3: Input(id_enum.Wire.SILVER_INSULATED),
            4: Input(id_enum.BatteryMatrix.FRAME),
            5: Input(id_enum.Wire.SILVER_INSULATED),
            7: Input(id_enum.ControlCircuit.ADVANCED),
        },
        id_enum.BatteryMatrix.CONTROLLER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        32,
    ),
    MRecipe(
        {
            0: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            1: Input(tag_enum.PlateTag.TIN, is_tag=True),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.Wire.SILVER_INSULATED),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
            8: Input(id_enum.Ingots.LIGHT_SKYBLUE),
        },
        id_enum.BatteryMatrix.IO_ENERGY_INPUT,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    MRecipe(
        {
            1: Input(tag_enum.PlateTag.TIN, is_tag=True),
            2: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.Wire.SILVER_INSULATED),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            6: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.BatteryMatrix.IO_ENERGY_OUTPUT,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    MRecipe(
        {
            0: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            1: Input(tag_enum.PlateTag.TIN, is_tag=True),
            2: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            3: Input(id_enum.Wire.SILVER_INSULATED),
            4: Input(id_enum.REDSTONEFLUX_CORE),
            5: Input(id_enum.Wire.SILVER_INSULATED),
            6: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
            8: Input(id_enum.Ingots.LIGHT_SKYBLUE),
        },
        id_enum.BatteryMatrix.CORE,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    # bedrock lava drill structure
    MRecipe(
        {
            0: Input(id_enum.ELECTRIC_MOTOR),
            1: Input(id_enum.ELECTRIC_MOTOR),
            2: Input(id_enum.ELECTRIC_MOTOR),
            3: Input(id_enum.Wire.SILVER_INSULATED),
            4: Input(id_enum.BedrockLavaDrill.FRAME),
            5: Input(id_enum.Wire.SILVER_INSULATED),
            7: Input(id_enum.ControlCircuit.ADVANCED),
        },
        id_enum.BedrockLavaDrill.CONTROLLER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        32,
    ),
    MRecipe(
        {
            1: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            3: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            4: Input(id_enum.Wire.SILVER),
            5: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            7: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
        },
        id_enum.BedrockLavaDrill.IO_ENERGY,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    MRecipe(
        {
            1: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            3: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            4: Input(id_enum.Pipe.ULTRAHEATINUM),
            5: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
            7: Input(tag_enum.PlateTag.ULTRAHEATINUM, is_tag=True),
        },
        id_enum.BedrockLavaDrill.IO_FLUID,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
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
        id_enum.Machinery.CHARGER,
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
        id_enum.Machinery.COMPRESSOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # deepslate lava vibrator
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            1: Input(tag_enum.StickTag.INVAR, is_tag=True),
            2: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            3: Input("minecraft:iron_bars"),
            4: Input("minecraft:heavy_core"),
            5: Input("minecraft:iron_bars"),
            6: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input(id_enum.REDSTONEFLUX_CORE),
            8: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.Machinery.DEEPSLATE_LAVA_VIBRATOR,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        24,
    ),
    # digger
    MRecipe(
        {
            1: Input(id_enum.DRILL_TOP_STEEL),
            3: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            4: Input(id_enum.ELECTRIC_MOTOR),
            5: Input(id_enum.Plates.STEEL),
            6: Input(id_enum.Wire.COPPER),
            7: Input(id_enum.Cable.STEEL),
            8: Input(id_enum.Wire.COPPER),
        },
        id_enum.Machinery.DIGGER,
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
        id_enum.Machinery.DISTILLATION_CHAMBER,
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
        id_enum.Machinery.ELECTRIC_CRAFTER,
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
        id_enum.Machinery.ELECTRIC_HEATER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # energy cube : junior
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.ALUMINUM, is_tag=True),
            1: Input(id_enum.Batteries.JUNIOR),
            2: Input(tag_enum.PlateTag.ALUMINUM, is_tag=True),
            3: Input(id_enum.Batteries.JUNIOR),
            4: Input(id_enum.SKYBLUE_CORE),
            5: Input(id_enum.Batteries.JUNIOR),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.Batteries.JUNIOR),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.ENERGY_CUBE_JUNIOR,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
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
        id_enum.Machinery.FARMING_STATION,
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
        id_enum.Machinery.FLUID_CONDENSER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # fluid splitter
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.TIN, is_tag=True),
            1: Input("minecraft:cauldron"),
            2: Input(tag_enum.PlateTag.TIN, is_tag=True),
            3: Input(id_enum.Pipe.CUPRONICKEL),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(id_enum.Pipe.CUPRONICKEL),
            6: Input("minecraft:iron_ingot"),
            7: Input(id_enum.Tank.STEEL),
            8: Input("minecraft:iron_ingot"),
        },
        id_enum.Machinery.FLUID_SPLITTER,
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
        id_enum.Machinery.FORESTER,
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
        id_enum.Machinery.FREEZER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # gas burning generator
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            1: Input(id_enum.REDSTONEFLUX_CORE),
            2: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            3: Input(id_enum.Wire.COPPER),
            4: Input(id_enum.HEAT_EXCHANGER),
            5: Input(id_enum.Wire.COPPER),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.GAS_BURNING_GENERATOR,
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
            3: Input(id_enum.Wire.COPPER_INSULATED),
            4: Input(id_enum.HEAT_EXCHANGER),
            5: Input(id_enum.Wire.COPPER_INSULATED),
            6: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
            7: Input("minecraft:hopper"),
            8: Input(tag_enum.PlateTag.CUPRONICKEL, is_tag=True),
        },
        id_enum.Machinery.GEO_THERMAL_GENERATOR,
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
        id_enum.Machinery.HOVER_TEXT_DISPLAYER,
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
        id_enum.Machinery.HYDROPONIC_BASE,
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
        id_enum.Machinery.HYDROPONIC_BED,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # hydroponic bed sand
    MRecipe(
        {
            0: Input("minecraft:glass_pane"),
            1: Input("minecraft:lantern"),
            2: Input("minecraft:glass_pane"),
            3: Input("minecraft:glass_pane"),
            5: Input("minecraft:glass_pane"),
            6: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            7: Input(id_enum.DUST_BLOCK),
            8: Input(tag_enum.PlateTag.STEEL, is_tag=True),
        },
        id_enum.Machinery.HYDROPONIC_BED_SAND,
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
        id_enum.Machinery.ITEM_SPLITTER,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # item spreader
    MRecipe(
        {
            0: Input(tag_enum.PlateTag.TIN, is_tag=True),
            1: Input("minecraft:hopper"),
            2: Input(tag_enum.PlateTag.TIN, is_tag=True),
            3: Input(id_enum.Cable.STEEL),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(id_enum.Cable.STEEL),
            6: Input("minecraft:iron_ingot"),
            7: Input("minecraft:piston"),
            8: Input("minecraft:iron_ingot"),
        },
        id_enum.Machinery.ITEM_SPLITTER,
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
        id_enum.Machinery.MACERATOR,
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
        id_enum.Machinery.MAGMA_CENTRIFUGE,
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
        id_enum.Machinery.MAGMA_FURNACE,
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
        id_enum.Machinery.METAL_PRESS,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # mini miner
    MRecipe(
        {
            1: Input(id_enum.ELECTRIC_MOTOR),
            3: Input(tag_enum.PlateTag.INVAR, is_tag=True),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.INVAR, is_tag=True),
            6: Input(tag_enum.StickTag.INVAR, is_tag=True),
            7: Input(id_enum.DRILL_TOP_STEEL),
            8: Input(tag_enum.StickTag.INVAR, is_tag=True),
        },
        id_enum.Machinery.MINI_MINER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        16,
    ),
    # mixed macerator
    MRecipe(
        {
            0: Input(id_enum.Coils.COPPER),
            1: Input(id_enum.ELECTRIC_MOTOR),
            2: Input(id_enum.Coils.COPPER),
            3: Input("minecraft:flint"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:flint"),
            6: Input(id_enum.Sticks.STEEL),
            7: Input(id_enum.ControlCircuit.ADVANCED),
            8: Input(id_enum.Sticks.STEEL),
        },
        id_enum.Machinery.MIXED_MACERATOR,
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
        id_enum.Machinery.MIXER,
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
        id_enum.Machinery.OIL_EXTRACTOR,
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
        id_enum.Machinery.PUMP,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # reacting thermal generator
    MRecipe(
        {
            0: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            1: Input(id_enum.REDSTONEFLUX_CORE),
            2: Input(id_enum.Ingots.LIGHT_SKYBLUE),
            3: Input(id_enum.Tank.BRONZE),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(id_enum.Tank.STEEL),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input("minecraft:cauldron"),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.REACTING_THERMAL_GENERATOR,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        12,
    ),
    # redstone furnace
    MRecipe(
        {
            1: Input("minecraft:furnace"),
            3: Input(id_enum.HEAT_PLATE),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input(tag_enum.PlateTag.COPPER, is_tag=True),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.ControlCircuit.BASIC),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.REDSTONE_FURNACE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # redstone generator
    MRecipe(
        {
            1: Input(id_enum.REDSTONEFLUX_CORE),
            3: Input("minecraft:copper_ingot"),
            4: Input(id_enum.MACHINERY_FRAME),
            5: Input("minecraft:copper_ingot"),
            6: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input("minecraft:repeater"),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.REDSTONE_GENERATOR,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # redstoneflux brake
    MRecipe(
        {
            0: Input("minecraft:redstone"),
            1: Input("minecraft:quartz"),
            2: Input("minecraft:redstone"),
            3: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            4: Input(id_enum.REDSTONEFLUX_CORE),
            5: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            6: Input(id_enum.Wire.TIN_INSULATED),
            7: Input("minecraft:target"),
            8: Input(id_enum.Wire.TIN_INSULATED),
        },
        id_enum.Machinery.REDSTONEFLUX_BRAKE,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # rf repeater plant
    MRecipe(
        {
            1: Input(tag_enum.PlateTag.STEEL, is_tag=True),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(tag_enum.StickTag.SUPERCONDUCT, is_tag=True),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            7: Input(id_enum.Machinery.MACHINERY_BASE_LIGHT),
        },
        id_enum.Machinery.RF_REPEATER_PLANT,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        8,
    ),
    # solar panel
    MRecipe(
        {
            1: Input("skybluetech:solar_panel_pane"),
            4: Input(tag_enum.StickTag.TIN, is_tag=True),
            7: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.SOLAR_PANEL,
        MRecipe.LEVEL_IRON,
        MRecipe.LEVEL_IRON,
        8,
    ),
    # template assembler
    MRecipe(
        {
            0: Input("minecraft:redstone"),
            1: Input("minecraft:piston"),
            2: Input("minecraft:redstone"),
            3: Input(tag_enum.PlateTag.TIN, is_tag=True),
            4: Input(id_enum.Machinery.COMPRESSOR),
            5: Input(tag_enum.PlateTag.TIN, is_tag=True),
            6: Input(tag_enum.IngotTag.STEEL, is_tag=True),
            7: Input(id_enum.REDSTONEFLUX_CORE),
            8: Input(tag_enum.IngotTag.STEEL, is_tag=True),
        },
        id_enum.Machinery.TEMPLATE_ASSEMBLER,
        MRecipe.LEVEL_INVAR,
        MRecipe.LEVEL_INVAR,
        16,
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
        id_enum.Machinery.THERMAL_GENERATOR,
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
            7: Input(id_enum.Machinery.MACHINERY_BASE_LIGHT),
            8: Input(tag_enum.PlateTag.TIN, is_tag=True),
        },
        id_enum.Machinery.WIND_GENERATOR,
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
