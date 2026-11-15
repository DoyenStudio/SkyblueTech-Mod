# coding=utf-8
from ...misc.inscriber_press import EMPTY, STICK, STICK_GRID
from ..core import Recipe, Input, Output, CategoryType, RegisterRecipe


class InscriberPressRecipe(Recipe):
    recipe_icon_id = EMPTY

    def __init__(self, output_id, grid, input_id=EMPTY):
        # type: (str, list[int], str) -> None
        Recipe.__init__(self,
                        {CategoryType.ITEM: {0: Input(input_id)}},
                        {CategoryType.ITEM: {0: Output(output_id)}})
        self.input_id = input_id
        self.output_id = output_id
        self.grid = tuple(grid)

    def __hash__(self):
        return hash((self.input_id, self.output_id, self.grid))

    def __eq__(self, other):
        return (isinstance(other, InscriberPressRecipe)
                and (self.input_id, self.output_id, self.grid)
                == (other.input_id, other.output_id, other.grid))

    def Marshal(self):
        return dict(input_id=self.input_id, output_id=self.output_id, grid=list(self.grid))

    @classmethod
    def Unmarshal(cls, data):
        return cls(data["output_id"], data["grid"], data["input_id"])


RegisterRecipe(InscriberPressRecipe(STICK, STICK_GRID))
