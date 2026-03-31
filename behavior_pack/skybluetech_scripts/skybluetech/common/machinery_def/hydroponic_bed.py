# coding=utf-8
from ..define.id_enum import HYDROPONIC_BED
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.hydroponic_bed import HydroponicBedRecipe, Output


class HydroponicBedRecipesCollection(RecipesCollection):
    def __init__(self, recipes):
        # type: (dict[str, HydroponicBedRecipe]) -> None
        super(HydroponicBedRecipesCollection, self).__init__(
            HYDROPONIC_BED, *recipes.values()
        )
        self.recipes_mapping = recipes


recipes = HydroponicBedRecipesCollection({
    "minecraft:wheat_seeds": HydroponicBedRecipe(
        "minecraft:wheat",
        "minecraft:wheat_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:wheat")],
    ),
    "minecraft:carrot": HydroponicBedRecipe(
        "minecraft:carrots",
        "minecraft:carrot",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [],
    ),
    "minecraft:potato": HydroponicBedRecipe(
        "minecraft:potatoes",
        "minecraft:potato",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [],
    ),
    "minecraft:beetroot_seeds": HydroponicBedRecipe(
        "minecraft:beetroot",
        "minecraft:beetroot_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:beetroot")],
    ),
})
