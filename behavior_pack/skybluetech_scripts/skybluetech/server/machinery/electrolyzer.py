# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.electrolyzer import (
    FLUID_SLOT_MAX_VOLUMES, STORE_RF_MAX, recipes,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    MultiFluidContainer, Processor,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum


@RegisterMachine
class Electrolyzer(Processor, MultiFluidContainer):
    block_name = Machinery.ELECTROLYZER
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = recipes
    item_input_slots = (0,)  # Anode.
    item_output_slots = (1, 2)  # Cathode product, anode by-product.
    fluid_input_slots = (0,)
    fluid_output_slots = (1, 2, 3)
    fluid_output_slots_by_face = {
        RelativeFacingStrEnum.LEFT: (2,),
        RelativeFacingStrEnum.RIGHT: (1,),
        RelativeFacingStrEnum.DOWN: (3,),
    }
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    upgrade_slot_start = 3
    upgrade_slots = 4

    def _processor_on_ticking(self):
        # Charge once per powered tick and finish on the final processing tick.
        # The generic processor otherwise charges a further completion tick.
        if not self.IsActive() or self.current_recipe is None:
            return
        if not self.PowerEnough():
            return
        self.ReducePower()
        remaining = self.reduce_ticks
        while remaining > 0 and self.current_recipe is not None:
            consumed = min(remaining, self.ticks_left)
            self.ticks_left -= consumed
            remaining -= consumed
            if self.ticks_left > 0:
                break
            self.run_once()
            self.start_next()
            if not self.IsActive():
                break
        self.CallSync()
