# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.plugins.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
)
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.plugins.allitems_getter import GetItemsByTag, allitems_by_tag
from ...define.machine_config.define import MachineRecipe
from ..machines.utils import ItemDisplayer, FluidDisplayer

def RenderMachineRecipe(panel, recipe):
    # type: (UBaseCtrl, MachineRecipe) -> None
    input_items = recipe.inputs.get("item", {})
    for slot, input in input_items.items():
        item = input.id
        is_tag = input.is_tag
        if is_tag:
            try:
                item_id = next(iter(GetItemsByTag(item)))
            except StopIteration:
                raise ValueError("tag2item not found: " + item)
        else:
            item_id = item
        ItemDisplayer(
            panel["slot%d" % slot],
            Item(item_id, count=int(input.count)),
            tag=item if is_tag else None,
        )
    output_items = recipe.outputs.get("item", {})
    for slot, input in output_items.items():
        item_id = input.id
        ItemDisplayer(panel["slot%d" % slot], Item(item_id, count=int(input.count)))
    input_fluids = recipe.inputs.get("fluid", {})
    if input_fluids:
        max_input_fluid_volume = max(input_fluids.values(), key=lambda x: x.count).count
    for slot, input in input_fluids.items():
        FluidDisplayer(
            panel["fluid%d" % slot],
            input.id, input.count, max_input_fluid_volume
        )
    output_fluids = recipe.outputs.get("fluid", {})
    if output_fluids:
        max_output_fluid_volume = max(output_fluids.values(), key=lambda x: x.count).count
    for slot, output in output_fluids.items():
        FluidDisplayer(
            panel["fluid%d" % slot],
            output.id, output.count, max_output_fluid_volume
        )


def RenderCraftingTableRecipe(panel, recipe):
    # type: (UBaseCtrl, CraftingRecipeRes | UnorderedCraftingRecipeRes) -> None
    if isinstance(recipe, CraftingRecipeRes):
        pat_mapping = recipe.pattern_key
        for row, rowln in enumerate(recipe.pattern):
            for col, pat in enumerate(rowln):
                if pat == " ":
                    continue
                item = pat_mapping[pat]
                ItemDisplayer(
                    panel["slot%d" % (row * 3 + col)],
                    Item(item.item_id, item.aux_value)
                )
    else:
        for i, input in enumerate(recipe.inputs):
            ItemDisplayer(panel["slot%d" % i], Item(input.item_id, input.aux_value))
    ItemDisplayer(panel["slot9"], Item(recipe.result[0].item_id, recipe.result[0].aux_value))

def RenderFurnaceRecipe(panel, recipe):
    # type: (UBaseCtrl, FurnaceRecipe) -> None
    ItemDisplayer(panel["slot0"], Item(recipe.input_item_id))
    ItemDisplayer(panel["slot1"], Item(recipe.output.item_id, recipe.output.aux_value))
