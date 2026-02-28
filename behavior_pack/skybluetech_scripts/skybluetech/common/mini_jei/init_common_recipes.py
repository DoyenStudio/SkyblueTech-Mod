# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    GetCraftingRecipe,
    GetFurnaceRecipe,
)
from skybluetech_scripts.tooldelta.api.client.world import (
    GetRecipesByResult,
)
from skybluetech_scripts.tooldelta.extensions.allitems_getter import AddItemGettedCallback
from .core.register import RegisterRecipe
from .common.recipe_cls import (
    GenericCraftingTableRecipe,
    GenericFurnaceRecipe,
)


items_from_recipe_loaded = set() # type: set[str]
reg_crafting_table_recipes = set() # type: set[GenericCraftingTableRecipe]
reg_furnace_recipes = set() # type: set[GenericFurnaceRecipe]

def RegisterItemToRecipe(item_id):
    # type: (str) -> None
    "按照给定物品生成一系列配方链。"
    if item_id in items_from_recipe_loaded:
        return
    items_from_recipe_loaded.add(item_id)
    # 工作台
    from_reses = GetRecipesByResult(item_id, "crafting_table")
    # BUG: 工作台配方会读取到多个相同配方
    # if "crafting_table" in str(from_reses):
    #     print("WARNING: !! crafting table from %s:" % item_id)
    #     import pprint
    #     pprint.pprint(from_reses)
    for res in from_reses:
        if "reagent" in res:
            # TODO: BUG: 接口会获取到酿造台配方
            print("[Warning] SkyblueTech: got brewing recipe from crafting_table: {}".format(res))
            continue
        rcp = GenericCraftingTableRecipe(GetCraftingRecipe(res))
        if rcp in reg_crafting_table_recipes:
            continue
        RegisterRecipe(rcp)
        reg_crafting_table_recipes.add(rcp)
        if isinstance(rcp.base, CraftingRecipeRes):
            for input in rcp.base.pattern_key.values():
                for item_id in input.item_ids:
                    RegisterItemToRecipe(item_id)
        else:
            for input in rcp.base.inputs:
                for item_id in input.item_ids:
                    RegisterItemToRecipe(item_id)
    # 熔炉
    from_reses = GetRecipesByResult(item_id, "furnace")
    for res in from_reses:
        rcp = GenericFurnaceRecipe(GetFurnaceRecipe(res))
        if rcp in reg_furnace_recipes:
            continue
        RegisterRecipe(rcp)
        reg_furnace_recipes.add(rcp)
        RegisterItemToRecipe(rcp.base.input_item_id)

def onItemsLoaded(item_ids):
    for item_id in item_ids:
        RegisterItemToRecipe(item_id)


AddItemGettedCallback(onItemsLoaded)
