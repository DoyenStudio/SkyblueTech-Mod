# coding=utf-8
import random
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from .define import (
    CategoryType,
    RecipesCollection,
    MachineRecipe,
    Input,
    Output,
)


class HydroponicBedSandRecipesCollection(RecipesCollection):
    def __init__(self, recipes):
        # type: (dict[str, HydroponicBedSandRecipe]) -> None
        super(HydroponicBedSandRecipesCollection, self).__init__(
            machinery.Machinery.HYDROPONIC_BED_SAND, *recipes.values()
        )
        self.recipes_mapping = recipes


class HydroponicBedSandRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.HYDROPONIC_BED_SAND

    def __init__(
        self,
        crop_block_id,  # type: str
        seed_item,  # type: str
        once_grow_progress,  # type: float
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
        self.once_grow_progress = once_grow_progress
        self.harvest_outputs = harvest_outputs

    def Marshal(self):
        # type: () -> dict
        result = {
            "crop_block_id": self.crop_block_id,
            "seed_item": self.seed_item,
            "once_grow_progress": self.once_grow_progress,
            "harvest_outputs": [output.to_dict() for output in self.harvest_outputs],
        }
        return result

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> HydroponicBedSandRecipe
        return cls(
            crop_block_id=data["crop_block_id"],
            seed_item=data["seed_item"],
            once_grow_progress=data["once_grow_progress"],
            harvest_outputs=[Output.from_dict(output) for output in data["harvest_outputs"]],
        )
