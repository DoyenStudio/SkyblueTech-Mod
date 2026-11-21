# coding=utf-8
from ...common.define.id_enum import GasMetallurgicalFurnace as ids
from ...common.machinery_def import gas_metallurgical_furnace as definition
from ...common.mini_jei.machinery.gas_metallurgical_furnace import GasMetallurgicalFurnaceRecipe
from .basic.multiblock_batch_processor import MultiblockBatchProcessor
from .core import RegisterMachine
from .gas_metallurgical_furnace_io import GasFurnaceIO, PORTS


@RegisterMachine
class GasMetallurgicalFurnace(GasFurnaceIO, MultiblockBatchProcessor):
    block_name = ids.CONTROLLER
    batch_key = definition.K_BATCH
    recipe_id_key = definition.K_RECIPE_ID
    batch_recipe_type = GasMetallurgicalFurnaceRecipe
    sync_on_work_tick = True
    store_rf_max = definition.STORE_RF_MAX
    recipes = definition.recipes
    process_item = True
    process_fluid = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    item_input_slots_by_face = {}
    item_output_slots_by_face = {}
    energy_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = (0, 1, 2)
    fluid_output_slots = (3, 4)
    fluid_slot_max_volumes = definition.FLUID_SLOT_MAX_VOLUMES
    upgrade_slots = 0
    allow_upgraders = frozenset()
    structure_palette = definition.STRUCTURE_PALETTE
    allow_unconfigured_structure = True
    functional_block_ids = set(port_id for port_id, cls in PORTS)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(GasMetallurgicalFurnace, self).__init__(dim, x, y, z, block_entity_data)
        self.bdata[definition.K_TEMPLATE_READY] = self.structure_palette is not None

    def _batch_step_and_cost(self, recipe, remaining):
        if remaining <= 0:
            return 0, 0
        return 1, recipe.tick_cost(self._work)
