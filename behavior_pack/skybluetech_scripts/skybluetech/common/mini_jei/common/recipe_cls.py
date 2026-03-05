# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
)
from ..core.define import CategoryType, RecipeBase
from ..core.render_utils import ItemDisplayer


class GenericCraftingTableRecipe(RecipeBase):
    recipe_icon_id = "minecraft:crafting_table"
    render_ui_def_name = "RecipeCheckerUI.crafting_table_recipes"

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

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        if isinstance(self.base, CraftingRecipeRes):
            pat_mapping = self.base.pattern_key
            for row, rowln in enumerate(self.base.pattern):
                for col, pat in enumerate(rowln):
                    if pat == " ":
                        continue
                    item = pat_mapping[pat]
                    ItemDisplayer(
                        panel["slot%d" % (row * 3 + col)],
                        Item(item.item_ids[0], item.aux_value),
                    )
        else:
            for i, input in enumerate(self.base.inputs):
                ItemDisplayer(
                    panel["slot%d" % i], Item(input.item_ids[0], input.aux_value)
                )
        ItemDisplayer(
            panel["slot9"],
            Item(
                self.base.result[0].item_id,
                self.base.result[0].aux_value,
                self.base.result[0].count,
            ),
        )

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        if ticks % 30:
            return
        if isinstance(self.base, CraftingRecipeRes):
            pat_mapping = self.base.pattern_key
            for row, rowln in enumerate(self.base.pattern):
                for col, pat in enumerate(rowln):
                    if pat == " ":
                        continue
                    input = pat_mapping[pat]
                    item_ids = input.item_ids
                    if len(item_ids) <= 1:
                        continue
                    ItemDisplayer(
                        panel["slot%d" % (row * 3 + col)],
                        Item(item_ids[ticks // 30 % len(item_ids)], input.aux_value),
                    )
        else:
            for i, input in enumerate(self.base.inputs):
                item_ids = input.item_ids
                if len(item_ids) <= 1:
                    continue
                ItemDisplayer(
                    panel["slot%d" % i],
                    Item(item_ids[ticks // 30 % len(item_ids)], input.aux_value),
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

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        # type: (UBaseCtrl, GenericFurnaceRecipe) -> None
        ItemDisplayer(panel["slot0"], Item(self.base.input_item_id))
        ItemDisplayer(
            panel["slot1"], Item(self.base.output.item_id, self.base.output.aux_value)
        )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        p = float(render_ticks % 300) / 300
        panel["progress/mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - p)

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
