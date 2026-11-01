# coding=utf-8
"""配方数据接口。集合与原实现共用，初始化时在两端分别扩展。"""
from ..mini_jei.core import (
    RecipesCollection, CategoryType, RecipeBase, Recipe, Input, Output,
    RegisterRecipe, MarshalOrderedInputs, MarshalOrderedOutputs, UnmarshalOrderedInputs, UnmarshalOrderedOutputs,
    MarshalUnorderedInputs, MarshalUnorderedOutputs,
    UnmarshalUnorderedInputs, UnmarshalUnorderedOutputs,
)
from ..mini_jei.machinery.define import MachineRecipeBase, MachineRecipe, GeneratorRecipe
from ..mini_jei.machinery.macerator import (
    MaceratorRecipe, gen_preset_recipe, gen_tagged_preset_recipe,
)
from ..mini_jei.machinery.magma_furnace import MagmaFurnaceRecipe
from ..mini_jei.machinery.redstone_generator import RedstoneGeneratorRecipe
from ..mini_jei.machinery.air_compressor import AirCompressorRecipe
from ..mini_jei.machinery.alloy_furnace import AlloyFurnaceRecipe
from ..mini_jei.machinery.charger import ChargerRecipe
from ..mini_jei.machinery.compressor import CompressorRecipe
from ..mini_jei.machinery.cyro_heat_melting_chamber import CyroHeatMeltingChamberRecipe
from ..mini_jei.machinery.distillation_chamber import DistillationChamberRecipe
from ..mini_jei.machinery.engraver import EngraverRecipe
from ..mini_jei.machinery.electrolyzer import ElectrolyzerRecipe
from ..mini_jei.machinery.fluid_condenser import FluidCondenserRecipe
from ..mini_jei.machinery.freezer import FreezerRecipe
from ..mini_jei.machinery.gas_burning_generator import GasBurningGeneratorRecipe
from ..mini_jei.machinery.hydroponic_bed import HydroponicBedRecipe
from ..mini_jei.machinery.hydroponic_bed_sand import HydroponicBedSandRecipe
from ..mini_jei.machinery.machinery_workstation import MachineryWorkstationRecipe
from ..mini_jei.machinery.magma_centrifuge import MagmaCentrifugeRecipe
from ..mini_jei.machinery.metal_press import MetalPressRecipe
from ..mini_jei.machinery.mixed_macerator import MixedMaceratorRecipe
from ..mini_jei.machinery.mixer import MixerRecipe
from ..mini_jei.machinery.oil_extractor import OilExtractorRecipe
from ..mini_jei.machinery.precision_cutter import PrecisionCutterRecipe
from ..mini_jei.machinery.reacting_thermal_generator import ReactingThermalGeneratorRecipe
from ..mini_jei.machinery.sawmill import SawmillRecipe
from ..mini_jei.machinery.template_assembler import TemplateAssemblerRecipe
from ..mini_jei.machinery.vacuum_freezer import VacuumFreezerRecipe
from ..mini_jei.misc.industrial_researching import IndustrialResearchingRecipe
from ..mini_jei.misc.metal_hammer import MetalHammerRecipe
from ..mini_jei.common.common_recipe_cls import (
    GenericCraftingTableRecipe, GenericFurnaceRecipe,
    GenericBlastFurnaceRecipe, GenericSmokerRecipe,
)
from ..mini_jei.common.description import Description, RegisterDescription
from ..mini_jei.core.helper import GetRecipesByInput, GetRecipesByOutput, GetRecipesByCategory

__all__ = [
    "RecipesCollection", "CategoryType", "RecipeBase", "Recipe", "Input", "Output",
    "RegisterRecipe", "MarshalOrderedInputs", "MarshalOrderedOutputs", "UnmarshalOrderedInputs",
    "UnmarshalOrderedOutputs", "MachineRecipeBase", "MachineRecipe", "GeneratorRecipe",
    "MarshalUnorderedInputs", "MarshalUnorderedOutputs",
    "UnmarshalUnorderedInputs", "UnmarshalUnorderedOutputs",
    "MaceratorRecipe", "MagmaFurnaceRecipe", "RedstoneGeneratorRecipe",
    "gen_preset_recipe", "gen_tagged_preset_recipe",
    "GetRecipesByInput", "GetRecipesByOutput", "GetRecipesByCategory",
    "AirCompressorRecipe", "AlloyFurnaceRecipe", "ChargerRecipe", "CompressorRecipe",
    "CyroHeatMeltingChamberRecipe", "DistillationChamberRecipe", "EngraverRecipe",
    "ElectrolyzerRecipe", "FluidCondenserRecipe", "FreezerRecipe", "GasBurningGeneratorRecipe",
    "HydroponicBedRecipe", "HydroponicBedSandRecipe", "MachineryWorkstationRecipe",
    "MagmaCentrifugeRecipe", "MetalPressRecipe", "MixedMaceratorRecipe", "MixerRecipe",
    "OilExtractorRecipe", "PrecisionCutterRecipe", "ReactingThermalGeneratorRecipe",
    "SawmillRecipe", "TemplateAssemblerRecipe", "VacuumFreezerRecipe",
    "IndustrialResearchingRecipe", "MetalHammerRecipe", "GenericCraftingTableRecipe",
    "GenericFurnaceRecipe", "GenericBlastFurnaceRecipe", "GenericSmokerRecipe",
    "Description", "RegisterDescription",
]
