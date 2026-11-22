# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery, Upgraders
from skybluetech_scripts.skybluetech.common.machinery_def.small_chemical_reactor import (
    STORE_RF_MAX, FLUID_SLOT_MAX_VOLUMES, recipes,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import Processor, MultiFluidContainer
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from .basic.fluid_output_faces import FluidOutputFaces


@RegisterMachine
class SmallChemicalReactor(FluidOutputFaces, Processor, MultiFluidContainer):
    block_name = Machinery.SMALL_CHEMICAL_REACTOR
    store_rf_max = STORE_RF_MAX
    process_item = True
    process_fluid = True
    recipes = recipes
    fluid_input_slots = (0, 1)
    fluid_output_slots = (2,)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    item_input_slots = (0, 2)
    item_output_slots = (1,)
    upgrade_slot_start = 3
    upgrade_slots = 1
    allow_upgraders = frozenset((Upgraders.GENERIC_AUTO_EJECTION,))
