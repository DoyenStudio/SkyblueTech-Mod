# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define import flags
from ...common.define.id_enum.machinery import REDSTONE_GENERATOR as MACHINE_ID
from ...common.machinery_def.redstone_generator import recipes as Recipes
from ...common.ui_sync.machinery.redstone_generator import RedstoneGeneratorUISync
from .basic import (
    GeneratorProcessor,
    RegisterMachine,
)

K_BURN_TICKS_LEFT = "st:burn_ticks_left"
K_MAX_BURN_TICKS = "st:max_burn_ticks"
K_LAST_BURNING_ITEM = "st:last_burning_item"


@RegisterMachine
class RedstoneGenerator(GeneratorProcessor):
    block_name = MACHINE_ID
    store_rf_max = 14400
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = RedstoneGeneratorUISync.NewServer(self).Activate()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.rest_burn_relative = (
            1 - self.GetProcessProgress() if self.current_recipe is not None else 0
        )
        self.sync.MarkedAsChanged()
