# coding=utf-8
from ..define import id_enum as ids
from ..define.id_enum import fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import Input, Output
from ..mini_jei.machinery.gas_metallurgical_furnace import GasMetallurgicalFurnaceRecipe
from ..utils.phys_math import Thermal
from ..utils.structure_palette import GenerateSimpleStructureTemplate

STORE_RF_MAX = 64000
GAS_INPUT = 0
AUX_GAS_INPUT = 1
LIQUID_INPUT = 2
GAS_OUTPUT = 3
LIQUID_OUTPUT = 4
FLUID_SLOT_MAX_VOLUMES = {0: 8000, 1: 8000, 2: 8000, 3: 16000, 4: 8000}
K_BATCH = "st:gas_furnace_batch"
K_RECIPE_ID = "st:gas_furnace_recipe"
K_TEMPLATE_READY = "st:gas_furnace_template_ready"

_GMF = ids.GasMetallurgicalFurnace

# 3×3×5；# 所在层为控制器基准，. 为空气，底顶使用重型钢机械底座。
STRUCTURE_PALETTE_DICT = {
    -2: [
        "HHH",
        "HHH",
        "HHH",
    ],
    -1: ["iii", "i.i", "iii"],
    0: ["i#i", "i.i", "iii"],
    1: ["ooo", "o.o", "ooo"],
    2: [
        "HHH",
        "HHH",
        "HHH",
    ],
}
STRUCTURE_KEYS = {
    "H": ids.HEAVY_STEEL_MACHINE_BASE,
    "F": _GMF.FRAME,
    "i": [
        _GMF.FRAME,
        _GMF.IO_ENERGY_INPUT,
        _GMF.IO_FLUID_INPUT,
        _GMF.IO_GAS_INPUT,
        _GMF.IO_GAS_INPUT_AUXILIARY,
        _GMF.IO_ITEM_INPUT,
    ],
    "o": [_GMF.FRAME, _GMF.IO_GAS_OUTPUT, _GMF.IO_ITEM_OUTPUT, _GMF.IO_FLUID_OUTPUT],
}
STRUCTURE_REQUIRE_BLOCKS = {}
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    STRUCTURE_KEYS,
    STRUCTURE_PALETTE_DICT,
    "#",
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)


def batch(
    recipe_id,
    title,
    ticks,
    heat=0,
    power=0,
    item_in=None,
    item_out=None,
    gas_in=None,
    aux_gas=None,
    liquid_in=None,
    gas_out=None,
    liquid_out=None,
):
    inputs, outputs = {}, {}
    if item_in is not None:
        inputs["item"] = {0: item_in}
    if item_out is not None:
        outputs["item"] = {1: item_out}
    input_fluids = dict(
        (slot, value)
        for slot, value in (
            (GAS_INPUT, gas_in),
            (AUX_GAS_INPUT, aux_gas),
            (LIQUID_INPUT, liquid_in),
        )
        if value is not None
    )
    output_fluids = dict(
        (slot, value)
        for slot, value in ((GAS_OUTPUT, gas_out), (LIQUID_OUTPUT, liquid_out))
        if value is not None
    )
    if input_fluids:
        inputs["fluid"] = input_fluids
    if output_fluids:
        outputs["fluid"] = output_fluids
    total_rf = int(Thermal.ElectricCostOfHeat(heat)) + power * ticks
    return GasMetallurgicalFurnaceRecipe(
        recipe_id, title, inputs, outputs, total_rf, ticks
    )


recipes = RecipesCollection(
    ids.GasMetallurgicalFurnace.CONTROLLER,
    batch(
        "fe_reduce",
        "氧化铁氢还原",
        100,
        heat=1000,
        item_in=Input(ids.Dusts.IRON_OXIDE),
        item_out=Output(ids.Dusts.IRON),
        gas_in=Input(fluids.CommonGas.HYDROGEN, 100),
        gas_out=Output(fluids.CommonGas.WATER_VAPOR, 100),
    ),
    batch(
        "sn4",
        "锡石氢还原",
        160,
        heat=2000,
        item_in=Input(ids.Dusts.PURIFIED_CASSITERITE),
        item_out=Output(ids.Dusts.TIN),
        gas_in=Input(fluids.CommonGas.HYDROGEN, 200),
        gas_out=Output(fluids.CommonGas.WATER_VAPOR, 200),
    ),
    batch(
        "pb4",
        "氧化铅氢还原",
        100,
        heat=800,
        item_in=Input(ids.Dusts.LEAD_OXIDE),
        item_out=Output(ids.Dusts.LEAD),
        gas_in=Input(fluids.CommonGas.HYDROGEN, 100),
        gas_out=Output(fluids.CommonGas.WATER_VAPOR, 100),
    ),
    batch(
        "ag6",
        "氯化银氢还原",
        100,
        heat=1000,
        item_in=Input(ids.FilterCakes.SILVER_CHLORIDE),
        item_out=Output(ids.Dusts.SILVER),
        gas_in=Input(fluids.CommonGas.HYDROGEN, 50),
        gas_out=Output(fluids.Acid.HYDROGEN_CHLORIDE, 20),
    ),
    batch(
        "pt6",
        "氯铂液氢还原",
        200,
        heat=400,
        power=256,
        liquid_in=Input(fluids.Chemical.PLATINUM_SOLUTION, 250),
        item_out=Output(ids.Dusts.PLATINUM),
        gas_in=Input(fluids.CommonGas.HYDROGEN, 100),
        liquid_out=Output(fluids.Chemical.BARREN_HCL, 200),
    ),
    batch(
        "fe_dehydrate",
        "氢氧化铁焙烧",
        100,
        power=100,
        item_in=Input(ids.FilterCakes.IRON_HYDROXIDE),
        item_out=Output(ids.Dusts.IRON_OXIDE),
    ),
    batch(
        "al7",
        "氢氧化铝焙烧",
        200,
        power=100,
        item_in=Input(ids.FilterCakes.ALUMINUM_HYDROXIDE),
        item_out=Output(ids.Dusts.ALUMINUM_OXIDE),
    ),
    batch(
        "ti7",
        "水合氧化钛焙烧",
        200,
        power=100,
        item_in=Input(ids.FilterCakes.HYDRATED_TITANIUM_OXIDE),
        item_out=Output(ids.Dusts.TITANIUM_OXIDE),
    ),
    batch(
        "pb1",
        "粗铅氧化焙烧",
        200,
        heat=4000,
        item_in=Input(ids.RawOres.LEAD),
        item_out=Output(ids.Dusts.LEAD_OXIDE, 4),
        gas_in=Input(fluids.CommonGas.OXYGEN, 600),
        gas_out=Output(fluids.ChemicalGas.SULFUR_DIOXIDE, 400),
    ),
    batch(
        "pb2",
        "预选铅料氧化焙烧",
        200,
        heat=4000,
        item_in=Input(ids.SortedOres.LEAD),
        item_out=Output(ids.Dusts.LEAD_OXIDE, 4),
        gas_in=Input(fluids.CommonGas.OXYGEN, 600),
        gas_out=Output(fluids.ChemicalGas.SULFUR_DIOXIDE, 400),
    ),
    batch(
        "pb3",
        "铅精矿氧化焙烧",
        100,
        heat=1000,
        item_in=Input(ids.FineConcentrates.LEAD),
        item_out=Output(ids.Dusts.LEAD_OXIDE),
        gas_in=Input(fluids.CommonGas.OXYGEN, 150),
        gas_out=Output(fluids.ChemicalGas.SULFUR_DIOXIDE, 100),
    ),
    batch(
        "ti9",
        "钛料氯化与尾气氧化",
        150,
        heat=2000,
        item_in=Input(ids.Mixtures.TITANIUM_CHLORINATION),
        gas_in=Input(fluids.CommonGas.CHLORINE, 200),
        aux_gas=Input(fluids.CommonGas.OXYGEN, 100),
        liquid_out=Output(fluids.Chemical.CRUDE_TICL4, 250),
        gas_out=Output(fluids.ChemicalGas.CARBON_DIOXIDE, 100),
    ),
    batch(
        "ti11",
        "四氯化钛镁还原",
        200,
        heat=3000,
        item_in=Input(ids.MAGNESIUM_PELLET, 2),
        item_out=Output(ids.TITANIUM_SPONGE),
        gas_in=Input(fluids.CommonGas.ARGON, 1),
        liquid_in=Input(fluids.Chemical.PURE_TICL4, 250),
        liquid_out=Output(fluids.Chemical.MOLTEN_MGCL2, 500),
    ),
    batch(
        "mg3",
        "氯化镁受控脱水",
        200,
        heat=2000,
        gas_in=Input(fluids.Acid.HYDROGEN_CHLORIDE, 50),
        liquid_in=Input(fluids.Chemical.MGCL2_SOLUTION, 250),
        gas_out=Output(fluids.ChemicalGas.ACID_VAPOR, 150),
        liquid_out=Output(fluids.Chemical.MOLTEN_MGCL2, 250),
    ),
    batch(
        "dry_sponge",
        "湿海绵干燥",
        100,
        power=100,
        item_in=Input("minecraft:wet_sponge"),
        item_out=Output("minecraft:sponge"),
        gas_out=Output(fluids.CommonGas.WATER_VAPOR, 10000),
    ),
    batch(
        "dry_kelp",
        "海带干燥",
        100,
        power=100,
        item_in=Input("minecraft:kelp"),
        item_out=Output("minecraft:dried_kelp"),
        gas_out=Output(fluids.CommonGas.WATER_VAPOR, 50),
    ),
)
RECIPES_BY_ID = dict((recipe.recipe_id, recipe) for recipe in recipes)
