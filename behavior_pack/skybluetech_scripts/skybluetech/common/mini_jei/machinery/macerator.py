# coding=utf-8
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class MaceratorRecipe(MachineRecipe):
    recipe_icon_id = machinery.MACERATOR
    render_ui_def_name = "RecipeCheckerLib.macerator_recipes"

    def __init__(self, input_id, output_id, output_count, power_cost, tick_duration):
        # type: (Input, str, int, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: input_id}},
            {CategoryType.ITEM: {1: Output(output_id, output_count)}},
            power_cost,
            tick_duration,
        )
        self.input_id = input_id
        self.output_id = output_id
        self.output_count = output_count

    def Marshal(self):
        return {
            "input_id": self.input_id.to_dict(),
            "output": {
                "id": self.output_id,
                "count": self.output_count,
            },
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_id=Input.from_dict(data["input_id"]),
            output_id=data["output"]["id"],
            output_count=data["output"]["count"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )


def gen_preset_recipe(
    power_cost,  # type: int
    tick_duration,  # type: int
):
    def generate_recipe(
        input,  # type: str
        input_count,  # type: int
        output,  # type: str
        output_count,  # type: int
    ):
        return MaceratorRecipe(
            Input(input, input_count), output, output_count, power_cost, tick_duration
        )

    return generate_recipe


def gen_tagged_preset_recipe(
    power_cost,  # type: int
    tick_duration,  # type: int
):
    def generate_recipe(
        input,  # type: str
        input_count,  # type: int
        output,  # type: str
        output_count,  # type: int
    ):
        return MaceratorRecipe(
            Input(input, input_count, is_tag=True),
            output,
            output_count,
            power_cost,
            tick_duration,
        )

    return generate_recipe
