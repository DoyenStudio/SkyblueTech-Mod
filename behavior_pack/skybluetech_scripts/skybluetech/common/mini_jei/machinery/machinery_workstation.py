# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from ....common.define.id_enum import machinery, items
from ....common.define.tag_enum import Wrench, Pincer
from ..core import (
    CategoryType,
    Recipe,
    Input,
    Output,
    MarshalInputs,
    UnmarshalInputs,
)


class MachineryWorkstationRecipe(Recipe):
    recipe_icon_id = machinery.MACHINERY_WORKSTATION

    LEVEL_IRON = 1
    LEVEL_INVAR = 2
    LEVEL_MAPPING = {
        LEVEL_IRON: "铁",
        LEVEL_INVAR: "殷钢",
    }

    def __init__(
        self, input_items, output_item_id, wrench_level, pincer_level, craft_times
    ):
        # type: (dict[int, Input], str, int, int, int) -> None
        Recipe.__init__(
            self,
            {CategoryType.ITEM: input_items},
            {CategoryType.ITEM: {0: Output(output_item_id)}},
        )
        self.input_items = input_items
        self.output_item_id = output_item_id
        self.wrench_level = wrench_level
        self.pincer_level = pincer_level
        self.craft_times = craft_times
        self.dyn_item_renderers = []

    def GetInputs(self):
        orig = Recipe.GetInputs(self)
        return orig

    def Marshal(self):
        # type: () -> dict
        return {
            "input_items": MarshalInputs({CategoryType.ITEM: self.input_items}),
            "output_item_id": self.output_item_id,
            "wrench_level": self.wrench_level,
            "pincer_level": self.pincer_level,
            "craft_times": self.craft_times,
        }

    @classmethod
    def Unmarshal(cls, data):
        return cls(
            input_items=UnmarshalInputs(data["input_items"])[CategoryType.ITEM],
            output_item_id=data["output_item_id"],
            wrench_level=data["wrench_level"],
            pincer_level=data["pincer_level"],
            craft_times=data["craft_times"],
        )

    @classmethod
    def from_dict(
        cls,
        data,  # type: dict | str
    ):
        if isinstance(data, str):
            from ..core.storage import recipesFrom

            rs = recipesFrom.get(CategoryType.ITEM, {}).get(data)
            if rs is None:
                raise ValueError("Can't find recipe for " + data)
            getted_recipe = None
            for rcp in rs:
                if isinstance(rcp, cls):
                    getted_recipe = rcp
                    break
            if getted_recipe is None:
                raise ValueError("Can't find recipe for " + data)
            return getted_recipe
        else:
            return cls(
                {int(k): Input.from_dict(v) for k, v in data["inputs"].items()},
                data["output"],
                data.get("wrench_level", 1),
                data.get("pincer_level", 1),
                data.get("craft_times", 1),
            )

    def __hash__(self):
        return hash(self.output_item_id)


PINCER_LEVEL2ITEM = {
    MachineryWorkstationRecipe.LEVEL_IRON: items.Pincer.IRON,
    MachineryWorkstationRecipe.LEVEL_INVAR: items.Pincer.INVAR,
}
WRENCH_LEVEL2ITEM = {
    MachineryWorkstationRecipe.LEVEL_IRON: items.Wrench.IRON,
    MachineryWorkstationRecipe.LEVEL_INVAR: items.Wrench.INVAR,
}


def get_wrench_level(wrench_item):
    # type: (Item) -> int
    tags = wrench_item.GetBasicInfo().tags
    if Wrench.INVAR in tags:
        return MachineryWorkstationRecipe.LEVEL_INVAR
    elif Wrench.IRON in tags:
        return MachineryWorkstationRecipe.LEVEL_IRON
    return 0


def get_pincer_level(pincer_item):
    # type: (Item) -> int
    tags = pincer_item.GetBasicInfo().tags
    if Pincer.INVAR in tags:
        return MachineryWorkstationRecipe.LEVEL_INVAR
    elif Pincer.IRON in tags:
        return MachineryWorkstationRecipe.LEVEL_IRON
    return 0


def get_spec_level_avail_wrenchs(level):
    # type: (int) -> list[Item]
    return [Item(v) for k, v in WRENCH_LEVEL2ITEM.items() if k >= level]


def get_spec_level_avail_pincers(level):
    # type: (int) -> list[Item]
    return [Item(v) for k, v in PINCER_LEVEL2ITEM.items() if k >= level]
