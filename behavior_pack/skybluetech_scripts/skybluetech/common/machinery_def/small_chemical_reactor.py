# coding=utf-8
from ..define.id_enum import Machinery, Dusts, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import CategoryType, Input, Output
from ..mini_jei.machinery.small_chemical_reactor import SmallChemicalReactorRecipe

STORE_RF_MAX = 32000
FLUID_SLOT_MAX_VOLUMES = {0: 2000, 1: 2000, 2: 2000}
recipes = RecipesCollection(
    Machinery.SMALL_CHEMICAL_REACTOR,
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.CommonGas.ETHYLENE, 400),
                              1: Input(fluids.CommonGas.OXYGEN, 40)}},
        {CategoryType.FLUID: {2: Output(fluids.HotFluid.MOLTEN_POLYETHYLENE, 144)}},
        power_cost=128, tick_duration=200,
    ),
    SmallChemicalReactorRecipe(
        {CategoryType.ITEM: {0: Input(Dusts.EVIL_UNDEAD)},
         CategoryType.FLUID: {0: Input(fluids.CommonLiquid.WATER, 500)}},
        {CategoryType.FLUID: {2: Output(fluids.CommonLiquid.EVIL_UNDEAD, 500)}},
        power_cost=40, tick_duration=80,
    ),
    # PM-R4：氯化氢吸收
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.Acid.HYDROGEN_CHLORIDE, 100),
                              1: Input(fluids.CommonLiquid.WATER, 50)}},
        {CategoryType.FLUID: {2: Output(fluids.Chemical.HYDROCHLORIC_ACID, 100)}},
        power_cost=256, tick_duration=30,
    ),
    # V1：植物油制捕收剂
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.CommonOil.VEGETABLE_OIL, 50),
                              1: Input(fluids.CommonLiquid.WATER, 50)}},
        {CategoryType.FLUID: {2: Output(fluids.Chemical.MINERAL_COLLECTOR, 100)}},
        power_cost=128, tick_duration=75,
    ),
    # P2：工艺水高级氧化
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.CommonLiquid.ORGANIC_WASTE, 100),
                              1: Input(fluids.CommonGas.OXYGEN, 50)}},
        {CategoryType.FLUID: {2: Output(fluids.CommonLiquid.PROCESS_WATER, 100)}},
        power_cost=256, tick_duration=300,
    ),
    # N4：氯化钙粉按整数消耗，保留原批量。
    SmallChemicalReactorRecipe(
        {CategoryType.ITEM: {0: Input(Dusts.CALCIUM_CHLORIDE)},
         CategoryType.FLUID: {0: Input(fluids.CommonLiquid.WATER, 1000)}},
        {CategoryType.FLUID: {2: Output(fluids.CommonLiquid.CONCRETE_ACCEL, 1000)}},
        power_cost=256, tick_duration=300,
    ),
    # PB6：二氧化硫氧化制酸
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.ChemicalGas.SULFUR_DIOXIDE, 50),
                              1: Input(fluids.Chemical.PEROXIDE, 50)}},
        {CategoryType.FLUID: {2: Output(fluids.Acid.SULFURIC_ACID, 50)}},
        power_cost=256, tick_duration=150,
    ),
)
