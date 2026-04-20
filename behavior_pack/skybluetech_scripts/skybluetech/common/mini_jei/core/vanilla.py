# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    GetCraftingRecipe,
    GetFurnaceRecipe,
)
from skybluetech_scripts.tooldelta.api.client.world import (
    GetRecipesByInput,
    GetRecipesByResult,
)
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from .register import RegisterRecipe
from .common_recipe_cls import (
    GenericCraftingTableRecipe,
    GenericFurnaceRecipe,
    GenericBlastFurnaceRecipe,
    GenericSmokerRecipe,
)


items_from_recipe_loaded = set()  # type: set[str]
# reg_crafting_table_recipes = set()  # type: set[GenericCraftingTableRecipe]
# reg_furnace_recipes = set()  # type: set[GenericFurnaceRecipe]
# reg_blast_furnace_recipes = set()  # type: set[GenericBlastFurnaceRecipe]
# reg_smoker_recipes = set()  # type: set[GenericSmokerRecipe]


def LoadItemRecipes(item_id):
    # type: (str) -> None
    if item_id.startswith("tag:"):
        tag_items = GetItemsByTag(item_id[4:])
        for tag_item in tag_items:
            LoadItemRecipes(tag_item)
        return
    if item_id in items_from_recipe_loaded:
        return
    items_from_recipe_loaded.add(item_id)
    # 工作台
    # BUG: 工作台配方会读取到多个相同配方
    # if "crafting_table" in str(from_reses):
    #     print("WARNING: !! crafting table from %s:" % item_id)
    #     import pprint
    #     pprint.pprint(from_reses)
    for res in GetRecipesByInput(item_id, "crafting_table"):
        if "reagent" in res:
            # TODO: BUG: 接口会获取到酿造台配方
            print(
                "[Warning] SkyblueTech: got brewing recipe from crafting_table: {}".format(
                    res
                )
            )
            continue
        RegisterRecipe(GenericCraftingTableRecipe(GetCraftingRecipe(res)))
    for res in GetRecipesByResult(item_id, "crafting_table"):
        if "reagent" in res:
            # TODO: BUG: 接口会获取到酿造台配方
            print(
                "[Warning] SkyblueTech: got brewing recipe from crafting_table: {}".format(
                    res
                )
            )
            continue
        RegisterRecipe(GenericCraftingTableRecipe(GetCraftingRecipe(res)))
    # 熔炉
    for res in GetRecipesByInput(item_id, "furnace"):
        RegisterRecipe(GenericFurnaceRecipe(GetFurnaceRecipe(res)))
    for res in GetRecipesByResult(item_id, "furnace"):
        RegisterRecipe(GenericFurnaceRecipe(GetFurnaceRecipe(res)))
    # 高炉
    for res in GetRecipesByInput(item_id, "blast_furnace"):
        RegisterRecipe(GenericBlastFurnaceRecipe(GetFurnaceRecipe(res)))
    for res in GetRecipesByResult(item_id, "blast_furnace"):
        RegisterRecipe(GenericBlastFurnaceRecipe(GetFurnaceRecipe(res)))
    # 烟熏炉
    for res in GetRecipesByInput(item_id, "smoker"):
        RegisterRecipe(GenericSmokerRecipe(GetFurnaceRecipe(res)))
    for res in GetRecipesByResult(item_id, "smoker"):
        RegisterRecipe(GenericSmokerRecipe(GetFurnaceRecipe(res)))
