# coding=utf-8
import time
from skybluetech_scripts.tooldelta.plugins.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
    GetCraftingRecipe,
    GetFurnaceRecipe,
)
from skybluetech_scripts.tooldelta.api.client.world import (
    GetRecipesByInput,
    GetRecipesByResult,
)
from skybluetech_scripts.tooldelta.plugins.allitems_getter import AddItemGettedCallback
from .define import CategoryType, RecipeBase
from .register import RegisterRecipe


class GenericCraftingTableRecipe(RecipeBase):
    recipe_icon_id = "minecraft:crafting_table"
    render_ui_def_name = "RecipeCheckerUI.crafting_table_recipes"

    def __init__(self, base):
        # type: (CraftingRecipeRes | UnorderedCraftingRecipeRes) -> None
        self.base = base

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        if isinstance(self.base, CraftingRecipeRes):
            return {CategoryType.ITEM: [
                v.item_id
                for v in self.base.pattern_key.values()
            ]}
        else:
            return {CategoryType.ITEM: [
                v.item_id
                for v in self.base.inputs
            ]}

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [
            v.item_id
            for v in self.base.result
        ]}

    def __hash__(self):
        return



class GenericFurnaceRecipe(RecipeBase):
    recipe_icon_id = "minecraft:furnace"
    render_ui_def_name = "RecipeCheckerUI.furnace_recipes"

    def __init__(self, base):
        # type: (FurnaceRecipe) -> None
        self.base = base

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [self.base.input_item_id]}

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [self.base.output.item_id]}



items_from_recipe_loaded = set() # type: set[str]

def RegisterItemToRecipe(item_id):
    # type: (str) -> None
    "按照给定物品生成一系列配方链。"
    if item_id in items_from_recipe_loaded:
        return
    items_from_recipe_loaded.add(item_id)
    # 工作台
    from_reses = GetRecipesByResult(item_id, "crafting_table")
    for res in from_reses:
        if "reagent" in res:
            # TODO: BUG: 接口会获取到酿造台配方
            continue
        rcp = GenericCraftingTableRecipe(GetCraftingRecipe(res))
        RegisterRecipe(rcp)
        if isinstance(rcp.base, CraftingRecipeRes):
            for input in rcp.base.pattern_key.values():
                RegisterItemToRecipe(input.item_id)
        else:
            for input in rcp.base.inputs:
                RegisterItemToRecipe(input.item_id)
    # 熔炉
    from_reses = GetRecipesByResult(item_id, "furnace")
    for res in from_reses:
        rcp = GenericFurnaceRecipe(GetFurnaceRecipe(res))
        RegisterRecipe(rcp)
        RegisterItemToRecipe(rcp.base.input_item_id)

def onItemsLoaded(item_ids):
    for item_id in item_ids:
        RegisterItemToRecipe(item_id)

AddItemGettedCallback(onItemsLoaded)