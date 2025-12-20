# coding=utf-8


class RecipeInput:
    def __init__(self, item_id, count, aux_value=0):
        # type: (str, int, int) -> None
        self.item_id = item_id
        self.count = count
        self.aux_value = aux_value

    @classmethod
    def from_dict(cls, dic):
        return cls(dic["item"], dic.get("count", 1), dic.get("data", 0))


class RecipeOutput:
    def __init__(self, item_id, count, aux_value=0):
        # type: (str, int, int) -> None
        self.item_id = item_id
        self.count = count
        self.aux_value = aux_value

    @classmethod
    def from_dict(cls, dic):
        return cls(
            dic["item"],
            dic.get("count", 1),
            dic.get("data", 0)
        )


class CraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.pattern = data["pattern"]  # type: list[str]
        self.pattern_key = {k: RecipeInput.from_dict(v) for k, v in data["key"].items()}  # type: dict[str, RecipeInput]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]] # type: list[RecipeOutput]


class UnorderedCraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.inputs = [RecipeInput.from_dict(v) for v in data["ingredients"]]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]]


class FurnaceRecipe:
    def __init__(self, data):
        self.input_item_id = data["input"]
        output = data["output"]
        if isinstance(output, str):
            datas = output.split(":")[-1]
            iname = datas[:-1]
            aux = datas[-1]
            self.output = RecipeOutput(":".join(iname), 1, int(aux))
        else:
            self.output = RecipeOutput.from_dict(output)


def GetCraftingRecipe(
    recipe_dict # type: dict
):
    return (
        CraftingRecipeRes(recipe_dict)
        if "pattern" in recipe_dict
        else UnorderedCraftingRecipeRes(recipe_dict)
    )

def GetFurnaceRecipe(recipe_dict):
    return FurnaceRecipe(recipe_dict)



