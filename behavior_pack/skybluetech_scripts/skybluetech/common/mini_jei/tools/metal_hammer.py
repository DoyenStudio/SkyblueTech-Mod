# coding=utf-8
from ...define.id_enum import METAL_HAMMER
from ..core import CategoryType, RecipesCollection, Recipe, Input, Output


class MetalHammerRecipesCollection(RecipesCollection):
    def __init__(self, *recipes):
        # type: (MetalHammerRecipe) -> None
        RecipesCollection.__init__(self, METAL_HAMMER, *recipes)
        self.recipes_mapping = {i.hammer_in.id: i for i in recipes}


class MetalHammerRecipe(Recipe):
    recipe_icon_id = METAL_HAMMER
    render_ui_def_name = "RecipeCheckerLib.metal_hammer_recipes"
    minijei_title = "金属锤锤锭获得"

    def __init__(self, input, output_id):
        # type: (Input, str) -> None
        Recipe.__init__(
            self,
            {CategoryType.ITEM: {0: input}},
            {CategoryType.ITEM: {0: Output(output_id)}},
        )
        self.hammer_in = input
        self.hammer_out = output_id

    def __hash__(self):
        return hash(self.hammer_in) ^ hash(self.hammer_out)

    def __eq__(self, other):
        if not isinstance(other, MetalHammerRecipe):
            return False
        return self.hammer_in == other.hammer_in and self.hammer_out == other.hammer_out
