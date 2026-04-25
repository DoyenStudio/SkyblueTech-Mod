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


items_to_recipe_input_loaded = set()  # type: set[str]
items_to_recipe_output_loaded = set()  # type: set[str]

SPECIAL_ITEM_AUXES = {
    "minecraft:piston": 1,
}

# reg_crafting_table_recipes = set()  # type: set[GenericCraftingTableRecipe]
# reg_furnace_recipes = set()  # type: set[GenericFurnaceRecipe]
# reg_blast_furnace_recipes = set()  # type: set[GenericBlastFurnaceRecipe]
# reg_smoker_recipes = set()  # type: set[GenericSmokerRecipe]


def LoadItemRecipes(item_id, get_input=False, get_output=False):
    # type: (str, bool, bool) -> None

    # TODO: get_input 和 get_output 同时使用会出现重复配方

    # 工作台
    # BUG: 工作台配方会读取到多个相同配方
    # if "crafting_table" in str(from_reses):
    #     print("WARNING: !! crafting table from %s:" % item_id)
    #     import pprint
    #     pprint.pprint(from_reses)
    if get_input and item_id not in items_to_recipe_input_loaded:
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
        # 熔炉
        for res in GetRecipesByInput(item_id, "furnace"):
            RegisterRecipe(GenericFurnaceRecipe(GetFurnaceRecipe(res)))
        # 高炉
        for res in GetRecipesByInput(item_id, "blast_furnace"):
            RegisterRecipe(GenericBlastFurnaceRecipe(GetFurnaceRecipe(res)))
        # 烟熏炉
        for res in GetRecipesByInput(item_id, "smoker"):
            RegisterRecipe(GenericSmokerRecipe(GetFurnaceRecipe(res)))

    if get_output and item_id not in items_to_recipe_output_loaded:
        spec_aux = SPECIAL_ITEM_AUXES.get(item_id, 0)
        for res in GetRecipesByResult(item_id, "crafting_table", aux_value=spec_aux):
            if "reagent" in res:
                # TODO: BUG: 接口会获取到酿造台配方
                print(
                    "[Warning] SkyblueTech: got brewing recipe from crafting_table: {}".format(
                        res
                    )
                )
                continue
            RegisterRecipe(GenericCraftingTableRecipe(GetCraftingRecipe(res)))
        for res in GetRecipesByResult(item_id, "furnace"):
            RegisterRecipe(GenericFurnaceRecipe(GetFurnaceRecipe(res)))
        for res in GetRecipesByResult(item_id, "blast_furnace"):
            RegisterRecipe(GenericBlastFurnaceRecipe(GetFurnaceRecipe(res)))
        for res in GetRecipesByResult(item_id, "smoker"):
            RegisterRecipe(GenericSmokerRecipe(GetFurnaceRecipe(res)))
