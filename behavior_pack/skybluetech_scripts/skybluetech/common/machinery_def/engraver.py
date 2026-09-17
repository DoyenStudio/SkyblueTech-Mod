# coding=utf-8
from ..define import id_enum
from ..mini_jei.core import RecipesCollection, Input
from ..mini_jei.machinery.engraver import EngraverRecipe

STORE_RF_MAX = 16000
FLUID_SLOT_MAX_VOLUMES = (1500, 1500)


recipes = RecipesCollection(
    id_enum.Machinery.ENGRAVER,
    EngraverRecipe(
        {
            0: Input("minecraft:gold_ingot"),
            1: Input(id_enum.ControlCircuit.BASIC),
            2: Input(id_enum.ROUGH_RUBBER),
            3: Input("minecraft:copper_ingot"),
        },
        fluid_input=Input(id_enum.CommonLiquid.DISTILLED_WATER, 200),
        output_item_id=id_enum.ControlCircuit.ADVANCED,
        output_count=1,
        power_cost=120,
        tick_duration=320,
        extra_fluid_input=Input(id_enum.Acid.SULFURIC_ACID, 40),
    ),
    EngraverRecipe(
        {
            0: Input(id_enum.POLISHED_DIAMOND),
            1: Input(id_enum.ControlCircuit.ADVANCED),
            2: Input(id_enum.ROUGH_RUBBER),
            3: Input(id_enum.Ingots.PLATINUM),
        },
        fluid_input=Input(id_enum.CommonGas.NITROGEN, 420),
        output_item_id=id_enum.ControlCircuit.PROFESSIONAL,
        output_count=1,
        power_cost=120,
        tick_duration=320,
        extra_fluid_input=Input(id_enum.Acid.SULFURIC_ACID, 40),
    ),
)  # type: RecipesCollection[EngraverRecipe]
