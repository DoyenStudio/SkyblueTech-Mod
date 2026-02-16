# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server.world import GetRecipesByInput
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    GetCraftingRecipe,
    CraftingRecipeRes,
)
from ..define import flags
from ..define.id_enum.machinery import SPLITTER as MACHINE_ID
from ..ui_sync.machinery.splitter import SplitterUISync
from .basic import (
    BaseMachine,
    ItemContainer,
    GUIControl,
    SPControl,
    WorkRenderer,
    RegisterMachine,
)

split_recipes = {}  # type: dict[str, str]
cant_split_recipes = set()  # type: set[str]


@RegisterMachine
class Splitter(GUIControl, ItemContainer, SPControl, WorkRenderer):
    block_name = MACHINE_ID
    store_rf_max = 8800
    origin_process_ticks = 20 * 8
    running_power = 30
    input_slots = (0,)
    output_slots = (1,)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        SPControl.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = SplitterUISync.NewServer(self).Activate()
        self.OnSync()
        self.TryStartNext()

    def OnTicking(self):
        while self.IsActive():
            self.OnSync()
            if self.ProcessOnce():
                self.runOnce()
                self.TryStartNext()
            else:
                break

    def TryStartNext(self):
        self.RequireItems()
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        expected_output = GetSplitResult(input_item.newItemName, input_item.newAuxValue)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return

    def runOnce(self):
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            raise ValueError("No input")
        expected_output = GetSplitResult(input_item.newItemName, input_item.newAuxValue)
        if expected_output is None:
            raise ValueError("Recipe ERROR")
        if not self.canOutput(expected_output, output_item):
            return
        self.finishOnce(input_item, output_item, expected_output)

    def finishOnce(self, input, output, expected_output):
        # type: (Item, Item | None, str) -> None
        input.count -= 1
        self.SetSlotItem(0, input)
        if output is not None:
            output_item = output
            output_item.count += 9
        else:
            output_item = Item(expected_output, count=9)
        self.SetSlotItem(1, output_item)

    def canOutput(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and output_slot_item.count + 9
            <= output_slot_item.GetBasicInfo().maxStackSize
        )

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProcessProgress()
        self.sync.MarkedAsChanged()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return True

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        if slot_pos == 1:
            return
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        expected_output = GetSplitResult(input_item.newItemName, input_item.newAuxValue)
        if expected_output is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        SPControl.SetDeactiveFlag(self, flag)
        WorkRenderer.SetDeactiveFlag(self, flag)

    def OnUnload(self):
        # type: () -> None
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)


def GetSplitResult(item_id, aux_value=0):
    # type: (str, int) -> str | None
    res = split_recipes.get(item_id)
    if res is not None:
        return res
    elif res in cant_split_recipes:
        return None
    recipes = GetRecipesByInput(item_id, "crafting_table", aux_value)
    for recipe in recipes:
        recipe = GetCraftingRecipe(recipe)
        if isinstance(recipe, CraftingRecipeRes):
            if recipe.pattern == ["A"] and len(recipe.result) == 1:
                output = recipe.result[0]
                if output.count == 9:
                    res = output.item_id
                    split_recipes[item_id] = res
                    return res
    cant_split_recipes.add(item_id)
    return None
