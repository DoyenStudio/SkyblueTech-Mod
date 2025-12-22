# coding=utf-8
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
from .core.register import RegisterRecipe
from .common.recipe_cls import (
    GenericCraftingTableRecipe,
    GenericFurnaceRecipe,
)


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
