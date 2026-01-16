# coding=utf-8


class RecipeInput:
    def __init__(self, item_id, count, aux_value=0, is_tag=False):
        # type: (str, int, int, bool) -> None
        self.item_id = item_id
        "当 is_tag=True 时表示物品标签"
        self.count = count
        self.aux_value = aux_value
        self.is_tag = is_tag

    @classmethod
    def from_dict(cls, dic):
        if isinstance(dic["item"], list):
            print("[WARNING] multiple recipes:", dic["item"])
            dic["item"] = dic["item"][0]
        return cls(dic["item"], dic.get("count", 1), dic.get("data", 0))

    def __hash__(self):
        return hash((self.item_id, self.count, self.aux_value))


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

    def __hash__(self):
        return hash((self.item_id, self.count, self.aux_value))


class CraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.pattern = data["pattern"]  # type: list[str]
        self.pattern_key = {k: RecipeInput.from_dict(v) for k, v in data["key"].items()}  # type: dict[str, RecipeInput]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]] # type: list[RecipeOutput]

    def __hash__(self):
        return hash((tuple(self.pattern), tuple(self.pattern_key.values()), tuple(self.result)))


class UnorderedCraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.inputs = [RecipeInput.from_dict(v) for v in data["ingredients"]]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]]

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.result)))


class FurnaceRecipe:
    def __init__(self, data):
        self.input_item_id = data["input"] # type: str
        output = data["output"]
        if isinstance(output, str):
            if output.count(":") > 1:
                datas = output.split(":")
                iname = datas[:-1]
                aux = datas[-1]
                self.output = RecipeOutput(":".join(iname), 1, int(aux))
            else:
                self.output = RecipeOutput(output, 1)
        else:
            self.output = RecipeOutput.from_dict(output)

    def __hash__(self):
        return hash((self.input_item_id, self.output))


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



