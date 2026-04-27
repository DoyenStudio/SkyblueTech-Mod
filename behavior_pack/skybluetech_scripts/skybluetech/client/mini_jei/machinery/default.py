# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    alloy_furnace,
    compressor,
    fluid_condenser,
    macerator,
    magma_centrifuge,
    magma_furnace,
    metal_press,
    mixer,
    oil_extractor,
    redstone_generator,
)
from .define import MachineRecipeRenderer, GeneratorRecipeRenderer

alloy_furnace.AlloyFurnaceRecipe.SetRenderer(
    type(
        "AlloyFurnaceRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.alloy_furnace_recipes",
            "recipe_icon_id": machinery.ALLOY_FURNACE,
        },
    )
)
compressor.CompressorRecipe.SetRenderer(
    type(
        "CompressorRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.compressor_recipes",
            "recipe_icon_id": machinery.COMPRESSOR,
        },
    )
)
fluid_condenser.FluidCondenserRecipe.SetRenderer(
    type(
        "FluidCondenserRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.fluid_condenser_recipes",
            "recipe_icon_id": machinery.FLUID_CONDENSER,
        },
    )
)
macerator.MaceratorRecipe.SetRenderer(
    type(
        "MaceratorRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.macerator_recipes",
            "recipe_icon_id": machinery.MACERATOR,
        },
    )
)
magma_centrifuge.MagmaCentrifugeRecipe.SetRenderer(
    type(
        "MagmaCentrifugeRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.magma_centrifuge_recipes",
            "recipe_icon_id": machinery.MAGMA_CENTRIFUGE,
        },
    )
)
magma_furnace.MagmaFurnaceRecipe.SetRenderer(
    type(
        "MagmaFurnaceRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.magma_furnace_recipes",
            "recipe_icon_id": machinery.MAGMA_FURNACE,
        },
    )
)
metal_press.MetalPressRecipe.SetRenderer(
    type(
        "MetalPressRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.metal_press_recipes",
            "recipe_icon_id": machinery.METAL_PRESS,
        },
    )
)
mixer.MixerRecipe.SetRenderer(
    type(
        "MixerRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.mixer_recipes",
            "recipe_icon_id": machinery.MIXER,
        },
    )
)
oil_extractor.OilExtractorRecipe.SetRenderer(
    type(
        "OilExtractorRecipeRenderer",
        (MachineRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.oil_extractor_recipes",
            "recipe_icon_id": machinery.OIL_EXTRACTOR,
        },
    )
)
redstone_generator.RedstoneGeneratorRecipe.SetRenderer(
    type(
        "RedstoneGeneratorRecipeRenderer",
        (GeneratorRecipeRenderer,),
        {
            "render_ui_def_name": "RecipeCheckerLib.redstone_generator_recipes",
            "recipe_icon_id": machinery.REDSTONE_GENERATOR,
        },
    )
)
