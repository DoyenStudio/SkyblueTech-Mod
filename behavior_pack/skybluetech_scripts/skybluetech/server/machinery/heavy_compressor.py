# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    GetCraftingRecipe,
)

from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.machinery_def.heavy_compressor import STORE_RF_MAX
from .basic import (
    BaseMachine,
    GUIControl,
    ItemContainer,
    SPControl,
    WorkRenderer,
)
from .core import RegisterMachine

compressed_recipes = {}  # type: dict[str, str]
cant_compressed_recipes = set()  # type: set[str]


@RegisterMachine
class HeavyCompressor(WorkRenderer, SPControl, ItemContainer, GUIControl):
    block_name = Machinery.HEAVY_COMPRESSOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    origin_process_ticks = 20 * 5  # 8s
    running_power = 30
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        super(HeavyCompressor, self).__init__(dim, x, y, z, block_entity_data)
        self.TryStartNext()
        self.handler.SubscribeOnTicking(self._heavy_compressor_on_ticking)
        self.handler.SubscribeOnSlotUpdate(self._heavy_compressor_on_slot_update)

    def _heavy_compressor_on_ticking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.run_once()
                self.TryStartNext()
            else:
                break

    def TryStartNext(self):
        input_item = self.GetSlotItem(0)
        output_item = self.GetSlotItem(1)
        if input_item is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
            return
        expected_output = GetCompressedResult(
            input_item.newItemName, input_item.newAuxValue
        )
        if expected_output is None or input_item.count < 9:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return

    def run_once(self):
        input_item = self.GetSlotItem(0, False)
        output_item = self.GetSlotItem(1, False)
        if input_item is None:
            raise ValueError("No input")
        expected_output = GetCompressedResult(
            input_item.newItemName, input_item.newAuxValue
        )
        if expected_output is None:
            raise ValueError("Recipe ERROR")
        if not self.canOutput(expected_output, output_item):
            return
        self.finish_once(input_item, output_item, expected_output)

    def finish_once(self, input, output, expected_output):
        # type: (Item, Item | None, str) -> None
        input.count -= 9
        self.SetSlotItem(0, input)
        if output is not None:
            output_item = output
            output_item.count += 1
        else:
            output_item = Item(expected_output)
        self.SetSlotItem(1, output_item)

    def canOutput(self, expected_output_item_id, output_slot_item):
        # type: (str, Item | None) -> bool
        return output_slot_item is None or (
            output_slot_item.newItemName == expected_output_item_id
            and not output_slot_item.StackFull()
        )

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            self._heavy_compressor_is_valid_input(slot, item),
        )
        return all(results)

    def _heavy_compressor_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        return True

    def _heavy_compressor_on_slot_update(self, slot_pos):
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
        expected_output = GetCompressedResult(
            input_item.newItemName, input_item.newAuxValue
        )
        if expected_output is None or input_item.count < 9:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        if not self.canOutput(expected_output, output_item):
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            return
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)


def GetCompressedResult(item_id, aux_value=0):
    # type: (str, int) -> str | None
    res = compressed_recipes.get(item_id)
    if res is not None:
        return res
    elif res in cant_compressed_recipes:
        return None
        recipes = CF.CreateRecipe(LEVEL_ID).GetRecipesByInput(
            item_id, "crafting_table", aux_value, -1
        )
    for recipe in recipes:
        recipe = GetCraftingRecipe(recipe)
        if isinstance(recipe, CraftingRecipeRes):
            if recipe.pattern == ["AAA", "AAA", "AAA"]:
                result = recipe.result[0].item_id
                compressed_recipes[item_id] = result
                return result
        else:
            if len(recipe.inputs) == 1:
                first_item = recipe.inputs[0]
                if first_item.count == 9:
                    res = first_item.item_ids[0]
                    compressed_recipes[item_id] = res
                    return res
        # pattern = recipe.get("pattern")
        # ingredients = recipe.get("ingredients")
        # if pattern is not None:
        #     if pattern == ["AAA", "AAA", "AAA"]:
        #         result = recipe["result"][0]["item"]
        #         compressed_recipes[item_id] = result
        #         return result
        # elif ingredients is not None:
        #     if len(ingredients) == 1:
        #         first_item = ingredients[0]
        #         if first_item["count"] == 9:
        #             result = first_item["item"]
        #             compressed_recipes[item_id] = result
        #             return result
    cant_compressed_recipes.add(item_id)
    return None
