# coding=utf-8
from ..define.id_enum import Machinery, fluids
from .electrolyzer import (
    CHLOR_ALKALI_HYDROGEN_VOLUME,
    CHLOR_ALKALI_CHLORINE_VOLUME,
    CHLOR_ALKALI_POWER_COST,
    CHLOR_ALKALI_TICK_DURATION,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.gas_burning_generator import (
    GeneratorRecipe,
    GasBurningGeneratorRecipe,
)

MAX_INPUT_GAS_VOLUME = 2000
MAX_OUTPUT_GAS_VOLUME = 2000
STORE_RF_MAX = 28800

# Consume 3/100 of one shared electrolysis batch and recover 2/3 of its RF.
HCL_HYDROGEN_VOLUME = CHLOR_ALKALI_HYDROGEN_VOLUME * 3.0 / 100
HCL_CHLORINE_VOLUME = CHLOR_ALKALI_CHLORINE_VOLUME * 3.0 / 100
_hcl_energy_numerator = CHLOR_ALKALI_POWER_COST * CHLOR_ALKALI_TICK_DURATION * 2
if _hcl_energy_numerator % 100:
    raise ValueError("Chlor-alkali energy must allow an exact integer HCl RF budget")
HCL_OUTPUT_POWER = _hcl_energy_numerator // 100


recipes = RecipesCollection(
    Machinery.GAS_BURNING_GENERATOR,
    GasBurningGeneratorRecipe(fluids.CommonGas.PURE_METHANE, 4, 160),
    GasBurningGeneratorRecipe(fluids.CommonGas.METHANE, 4, 160),
    # Electrolysis: 20 mB H2 costs 2,000 RF; 16 mB burning recovers 15/32.
    GasBurningGeneratorRecipe(fluids.CommonGas.HYDROGEN, 16, 750),
    # Append to preserve saved recipe indices.
    GasBurningGeneratorRecipe(
        fluids.CommonGas.HYDROGEN, HCL_HYDROGEN_VOLUME, HCL_OUTPUT_POWER,
        output_gas_id=fluids.Acid.HYDROGEN_CHLORIDE,
        output_gas_volume=HCL_HYDROGEN_VOLUME + HCL_CHLORINE_VOLUME,
        second_gas_id=fluids.CommonGas.CHLORINE,
        second_burning_volume=HCL_CHLORINE_VOLUME,
    ),
)  # type: RecipesCollection[GeneratorRecipe]
