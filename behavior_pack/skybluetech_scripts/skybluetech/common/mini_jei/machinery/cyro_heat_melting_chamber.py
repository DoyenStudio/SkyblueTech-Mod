# coding=utf-8
from ...define.id_enum import machinery
from .define import CategoryType, MachineRecipe, RecipesCollection, Input, Output


class CyroHeatMeltingChamberRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.CYRO_HEAT_MELTING_CHAMBER

    def __init__(
        self,
        input_item_id,  # type: str
        output_fluid,  # type: str
        output_volume,  # type: float
        min_temperature,  # type: float
        fit_temperature,  # type: float
        max_temperature,  # type: float
        tick_duration,  # type: int
        max_tick_speed,  # type: int
        waste=None,  # type: str | None
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_item_id, 1)}},
            {CategoryType.FLUID: {1: Output(output_fluid, output_volume)}},
            0,
            tick_duration=tick_duration,
        )
        self.input_item_id = input_item_id
        self.output_fluid = output_fluid
        self.output_volume = output_volume
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.fit_temperature = fit_temperature
        self.max_tick_speed = max_tick_speed
        self.waste = waste

    def Marshal(self):
        # type: () -> dict
        return {
            "input_item_id": self.input_item_id,
            "output_fluid": self.output_fluid,
            "output_volume": self.output_volume,
            "min_temperature": self.min_temperature,
            "fit_temperature": self.fit_temperature,
            "max_temperature": self.max_temperature,
            "tick_duration": self.tick_duration,
            "max_tick_speed": self.max_tick_speed,
            "waste": self.waste,
        }

    @classmethod
    def Unmarshal(cls, data):
        # type: (dict) -> CyroHeatMeltingChamberRecipe
        return CyroHeatMeltingChamberRecipe(
            input_item_id=data["input_item_id"],
            output_fluid=data["output_fluid"],
            output_volume=data["output_volume"],
            min_temperature=data["min_temperature"],
            fit_temperature=data["fit_temperature"],
            max_temperature=data["max_temperature"],
            tick_duration=data["tick_duration"],
            max_tick_speed=data["max_tick_speed"],
            waste=data["waste"],
        )


def c2k(c):
    # type: (float) -> float
    return c + 273


class CyroHeatMeltingChamberRecipeCollection(RecipesCollection):
    def __init__(self, collection_name, *recipes):
        # type: (str, CyroHeatMeltingChamberRecipe) -> None
        RecipesCollection.__init__(self, collection_name, *recipes)
        self.recipes_mapping = {recipe.input_item_id: recipe for recipe in recipes}
