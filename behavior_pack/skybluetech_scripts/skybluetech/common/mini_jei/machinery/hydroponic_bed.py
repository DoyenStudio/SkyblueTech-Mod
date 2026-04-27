# coding=utf-8
import random
from ....common.define.id_enum import machinery
from .define import (
    CategoryType,
    RecipesCollection,
    MachineRecipe,
    Input,
    Output,
)


class HydroponicBedRecipesCollection(RecipesCollection):
    def __init__(self, recipes):
        # type: (dict[str, HydroponicBedRecipe]) -> None
        super(HydroponicBedRecipesCollection, self).__init__(
            machinery.HYDROPONIC_BED, *recipes.values()
        )
        self.recipes_mapping = recipes


class HydroponicBedRecipe(MachineRecipe):
    recipe_icon_id = machinery.HYDROPONIC_BED

    def __init__(
        self,
        crop_block_id,  # type: str
        seed_item,  # type: str
        grow_stage_ticks,  # type: int
        stages,  # type: int
        seed_output_probs,  # type: list[float]
        harvest_outputs,  # type: list[Output]
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(seed_item, 1)}},
            {CategoryType.ITEM: {i + 1: j for i, j in enumerate(harvest_outputs)}},
            0,
            0,
        )
        self.crop_renderer = None
        self.crop_block_id = crop_block_id
        self.seed_item = seed_item
        self.grow_stage_ticks = grow_stage_ticks
        self.stages = stages
        self.seed_output_probs = seed_output_probs
        self.harvest_outputs = harvest_outputs

    def rand_seed_count(self):
        r = random.random()
        for i, prob in enumerate(self.seed_output_probs):
            r -= prob
            if r <= 0:
                return i + 0  # at least 1
        # ...
        return len(self.seed_output_probs)

    def rand_harvest_output(self):
        for output in self.harvest_outputs:
            if output.prob >= random.random():
                yield output


c2k = lambda c: c + 273
