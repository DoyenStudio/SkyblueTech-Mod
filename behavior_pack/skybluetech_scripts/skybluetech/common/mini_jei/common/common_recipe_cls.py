# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
)
from ..core.define import CategoryType, RecipeBase


class GenericCraftingTableRecipe(RecipeBase):
    recipe_icon_id = "minecraft:crafting_table"

    def __init__(self, base):
        # type: (CraftingRecipeRes | UnorderedCraftingRecipeRes) -> None
        self.base = base

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        if isinstance(self.base, CraftingRecipeRes):
            return {
                CategoryType.ITEM: [
                    i for v in self.base.pattern_key.values() for i in v.item_ids
                ]
            }
        else:
            return {
                CategoryType.ITEM: [i for v in self.base.inputs for i in v.item_ids]
            }

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [v.item_id for v in self.base.result]}

    def Marshal(self):
        # type: () -> dict
        return {
            "base_data": self.base.data,
            "shaped": isinstance(self.base, CraftingRecipeRes),
        }

    @classmethod
    def Unmarshal(cls, dct):
        # type: (dict) -> GenericCraftingTableRecipe
        if dct["shaped"]:
            return GenericCraftingTableRecipe(CraftingRecipeRes(dct["base_data"]))
        else:
            return GenericCraftingTableRecipe(
                UnorderedCraftingRecipeRes(dct["base_data"])
            )

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, GenericCraftingTableRecipe):
            return False
        return self.base == other.base

    def __hash__(self):
        # type: () -> int
        return hash(self.base)


class GenericFurnaceRecipe(RecipeBase):
    recipe_icon_id = "minecraft:furnace"

    def __init__(self, base):
        # type: (FurnaceRecipe) -> None
        self.base = base

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: self.base.input.item_ids}

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [self.base.output.item_id]}

    def Marshal(self):
        # type: () -> dict
        return {"base_data": self.base.data}

    @classmethod
    def Unmarshal(cls, dct):
        # type: (dict) -> GenericFurnaceRecipe
        return GenericFurnaceRecipe(FurnaceRecipe(dct["base_data"]))

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, GenericFurnaceRecipe):
            return False
        return self.base == other.base

    def __hash__(self):
        return hash(self.base)


class GenericBlastFurnaceRecipe(GenericFurnaceRecipe):
    recipe_icon_id = "minecraft:blast_furnace"


class GenericSmokerRecipe(GenericFurnaceRecipe):
    recipe_icon_id = "minecraft:smoker"
