# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    FurnaceRecipe,
)
from .define import CategoryType, RecipeBase

if 0:
    from ....client.ui.recipe_checker.render_utils import (
        ItemDisplayer as _ItemDisplayer,
    )
    from ....client.ui.recipe_checker.render_utils_advanced import (
        MultiItemsDisplayer as _MultiItemsDisplayer,
        InputDisplayer as _InputDisplayer,
    )


class GenericCraftingTableRecipe(RecipeBase):
    recipe_icon_id = "minecraft:crafting_table"
    render_ui_def_name = "RecipeCheckerLib.crafting_table_recipes"

    def __init__(self, base):
        # type: (CraftingRecipeRes | UnorderedCraftingRecipeRes) -> None
        self.base = base
        self.input_displayers = []  # type: list[_MultiItemsDisplayer]

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
        from ....client.ui.recipe_checker.render_utils import ItemDisplayer
        from ....client.ui.recipe_checker.render_utils_advanced import (
            MultiItemsDisplayer,
        )

        RecipeBase.RenderInit(self, panel)
        self.input_displayers = []
        if isinstance(self.base, CraftingRecipeRes):
            pat_mapping = self.base.pattern_key
            for row, rowln in enumerate(self.base.pattern):
                for col, pat in enumerate(rowln):
                    if pat == " ":
                        continue
                    input = pat_mapping[pat]
                    self.input_displayers.append(
                        MultiItemsDisplayer(
                            panel["slot%d" % (row * 3 + col)],
                            [Item(i) for i in input.item_ids],
                        )
                    )
        else:
            for i, input in enumerate(self.base.inputs):
                self.input_displayers.append(
                    MultiItemsDisplayer(
                        panel["slot%d" % i],
                        [Item(i) for i in input.item_ids],
                    )
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
        for item_displayer in self.input_displayers:
            item_displayer.tick(ticks)

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
    render_ui_def_name = "RecipeCheckerLib.furnace_recipes"

    def __init__(self, base):
        # type: (FurnaceRecipe) -> None
        self.base = base
        self.input_displayer = None  # type: _MultiItemsDisplayer | None

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: self.base.input.item_ids}

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        return {CategoryType.ITEM: [self.base.output.item_id]}

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        from ....client.ui.recipe_checker.render_utils import ItemDisplayer
        from ....client.ui.recipe_checker.render_utils_advanced import (
            MultiItemsDisplayer,
        )

        RecipeBase.RenderInit(self, panel)
        self.input_displayer = MultiItemsDisplayer(
            panel["slot0"],
            [Item(i) for i in self.base.input.item_ids],
        )
        ItemDisplayer(
            panel["slot1"], Item(self.base.output.item_id, self.base.output.aux_value)
        )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        p = float(render_ticks % 300) / 300
        panel["progress/mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - p)
        if self.input_displayer:
            self.input_displayer.tick(render_ticks)

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
