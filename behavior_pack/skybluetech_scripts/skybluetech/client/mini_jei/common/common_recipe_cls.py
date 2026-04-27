# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
)
from skybluetech_scripts.skybluetech.common.mini_jei.common.common_recipe_cls import (
    GenericCraftingTableRecipe,
    GenericFurnaceRecipe,
    GenericBlastFurnaceRecipe,
    GenericSmokerRecipe,
)
from ..core.define import RecipeRenderer
from ...ui.recipe_checker.render_utils import (
    ItemDisplayer as ItemDisplayer,
)
from ...ui.recipe_checker.render_utils_advanced import (
    MultiItemsDisplayer as MultiItemsDisplayer,
    InputDisplayer as InputDisplayer,
)


class GenericCraftingTableRecipeRenderer(RecipeRenderer):
    recipe_icon_id = "minecraft:crafting_table"
    render_ui_def_name = "RecipeCheckerLib.crafting_table_recipes"

    def __init__(self, recipe):
        # type: (GenericCraftingTableRecipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.input_displayers = []  # type: list[MultiItemsDisplayer]

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        base = self.recipe.base
        if isinstance(base, CraftingRecipeRes):
            pat_mapping = base.pattern_key
            for row, rowln in enumerate(base.pattern):
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
            for i, input in enumerate(base.inputs):
                self.input_displayers.append(
                    MultiItemsDisplayer(
                        panel["slot%d" % i],
                        [Item(i) for i in input.item_ids],
                    )
                )
        ItemDisplayer(
            panel["slot9"],
            Item(
                base.result[0].item_id,
                base.result[0].aux_value,
                base.result[0].count,
            ),
        )

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        if ticks % 30:
            return
        for item_displayer in self.input_displayers:
            item_displayer.tick(ticks)

    @classmethod
    def Unmarshal(cls, dct):
        # type: (dict) -> GenericCraftingTableRecipe
        if dct["shaped"]:
            return GenericCraftingTableRecipe(CraftingRecipeRes(dct["base_data"]))
        else:
            return GenericCraftingTableRecipe(
                UnorderedCraftingRecipeRes(dct["base_data"])
            )


class GenericFurnaceRecipeRenderer(RecipeRenderer):
    recipe_icon_id = "minecraft:furnace"
    render_ui_def_name = "RecipeCheckerLib.furnace_recipes"

    def __init__(self, recipe):
        # type: (GenericFurnaceRecipe) -> None
        super(GenericFurnaceRecipeRenderer, self).__init__(recipe)
        self.recipe = recipe
        self.input_displayer = None  # type: MultiItemsDisplayer | None

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self.input_displayer = MultiItemsDisplayer(
            panel["slot0"],
            [Item(i) for i in self.recipe.base.input.item_ids],
        )
        ItemDisplayer(
            panel["slot1"],
            Item(self.recipe.base.output.item_id, self.recipe.base.output.aux_value),
        )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        p = float(render_ticks % 300) / 300
        panel["progress/mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - p)
        if self.input_displayer:
            self.input_displayer.tick(render_ticks)


class GenericBlastFurnaceRecipeRenderer(GenericFurnaceRecipeRenderer):
    recipe_icon_id = "minecraft:blast_furnace"


class GenericSmokerRecipeRenderer(GenericFurnaceRecipeRenderer):
    recipe_icon_id = "minecraft:smoker"


GenericCraftingTableRecipe.SetRenderer(GenericCraftingTableRecipeRenderer)
GenericFurnaceRecipe.SetRenderer(GenericFurnaceRecipeRenderer)
GenericBlastFurnaceRecipe.SetRenderer(GenericBlastFurnaceRecipeRenderer)
GenericSmokerRecipe.SetRenderer(GenericSmokerRecipeRenderer)
