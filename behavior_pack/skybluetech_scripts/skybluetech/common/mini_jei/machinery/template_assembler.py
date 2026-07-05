# coding=utf-8
from ...define.id_enum import machinery, INSCRIBING_TEMPLATE
from ...define.tag_enum import IngotTag
from .define import CategoryType, RecipesCollection, MachineRecipe, Input, Output


class TemplateAssemblerRecipesCollection(RecipesCollection):
    def __init__(self, *recipes):
        # type: (TemplateAssemblerRecipe) -> None
        super(TemplateAssemblerRecipesCollection, self).__init__(
            machinery.Machinery.TEMPLATE_ASSEMBLER, *recipes
        )
        self.recipes_mapping = {recipe.output_item_id: recipe for recipe in recipes}


class TemplateAssemblerRecipe(MachineRecipe):
    recipe_icon_id = machinery.Machinery.TEMPLATE_ASSEMBLER

    def __init__(
        self,
        input_items,  # type: dict[int, Input]
        output_item_id,  # type: str
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        input_items = input_items.copy()
        input_items[10] = Input(IngotTag.SOLDERING, is_tag=True)
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: input_items},
            {CategoryType.ITEM: {11: Output(output_item_id)}},
            power_cost,
            tick_duration,
        )
        self.input_items = input_items
        self.output_item_id = output_item_id

    def GetInputs(self):
        inputs = self.inputs.copy()
        input_items = inputs[CategoryType.ITEM] = self.inputs[CategoryType.ITEM].copy()
        input_items[9] = Input(INSCRIBING_TEMPLATE)
        return {
            cat: [
                ("tag:" + input.id if input.is_tag else input.id)
                for input in slot2input.values()
            ]
            for cat, slot2input in inputs.items()
        }

    def Marshal(self):
        return {
            "input_items": {
                slot: input.to_dict() for slot, input in self.input_items.items()
            },
            "output_item_id": self.output_item_id,
            "power_cost": self.power_cost,
            "tick_duration": self.tick_duration,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_items={
                slot: Input.from_dict(input_dict)
                for slot, input_dict in data["input_items"].items()
            },
            output_item_id=data["output_item_id"],
            power_cost=data["power_cost"],
            tick_duration=data["tick_duration"],
        )
