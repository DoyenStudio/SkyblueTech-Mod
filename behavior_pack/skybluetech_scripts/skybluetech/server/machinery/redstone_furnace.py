# coding=utf-8
from skybluetech_scripts.tooldelta.api.server.world import GetRecipesByInput
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.recipe_obj import GetFurnaceRecipe

from ...common.define import flags
from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.redstone_furnace import STORE_RF_MAX, TICK_POWER
from .basic import (
    GUIControl,
    ItemContainer,
    UpgradeControl,
    WorkRenderer,
)
from .core import RegisterMachine


@RegisterMachine
class RedstoneFurnace(WorkRenderer, UpgradeControl, GUIControl):
    block_name = Machinery.REDSTONE_FURNACE
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    origin_process_ticks = 20 * 8  # 8s
    running_power = TICK_POWER
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4
    allow_upgraders = frozenset({
        Upgraders.BASIC_SPEED_UPGRADER,
        Upgraders.GENERIC_AUTO_EJECTION,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(RedstoneFurnace, self).__init__(dim, x, y, z, block_entity_data)
        self.try_start_next()
        self.handler.SubscribeOnTicking(self._redstone_furnace_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._redstone_furnace_on_slot_update)

    def _redstone_furnace_on_ticking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.run_once()
                self.try_start_next()
            else:
                break

    def try_start_next(self):
        input_item = self.GetSlotItem(0)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        expected_output = get_furnace_output_by_input(input_item.newItemName)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        if not self.CanOutputItems([Item(expected_output)]):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return

    def run_once(self):
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            raise ValueError("No input")
        expected_output = get_furnace_output_by_input(input_item.newItemName)
        if expected_output is None:
            raise ValueError("Recipe ERROR")
        if not self.CanOutputItems([Item(expected_output)]):
            return
        self.finish_once(input_item, output_item, expected_output)

    def finish_once(self, input, output, expected_output):
        # type: (Item, Item | None, str) -> None
        input.count -= 1
        self.SetSlotItem(0, input)
        if output is not None:
            output_item = output
            output_item.count += 1
        else:
            output_item = Item(expected_output)
        self.SetSlotItem(1, output_item)
        self.FlushOutputSlots([1])

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            UpgradeControl.IsValidInput(self, slot, item),
            self._redstone_furnace_is_valid_input(slot, item),
        )
        return all(results)

    def _redstone_furnace_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        if self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        return ItemContainer.IsValidInput(self, slot, item)

    def _redstone_furnace_on_slot_update(self, slot_pos):
        # type: (int) -> None
        input_item = self.GetSlotItem(0)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        expected_output = get_furnace_output_by_input(input_item.newItemName)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not self.CanOutputItems([Item(expected_output)]):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)


def get_furnace_output_by_input(item_id, aux_value=0):
    # type: (str, int) -> str | None
    res = GetRecipesByInput(item_id, "furnace", aux_value, maxResultNum=1)
    if len(res) < 1:
        return None
    else:
        return GetFurnaceRecipe(res[0]).output.item_id
