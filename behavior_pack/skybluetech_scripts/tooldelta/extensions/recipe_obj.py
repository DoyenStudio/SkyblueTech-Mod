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
            # print("[WARNING] multiple recipes:", dic["item"])
            dic["item"] = dic["item"][0]
        return cls(dic["item"], dic.get("count", 1), dic.get("data", 0))

    def copy(self):
        return RecipeInput(self.item_id, self.count, self.aux_value, self.is_tag)

    def __hash__(self):
        return hash((self.item_id, self.count, self.aux_value))

    def __eq__(self, other):
        if not isinstance(other, RecipeInput):
            return False
        return (
            self.item_id == other.item_id
            and self.count == other.count
            and self.aux_value == other.aux_value
            and self.is_tag == other.is_tag
        )


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

    def copy(self):
        return RecipeOutput(self.item_id, self.count, self.aux_value)

    def __hash__(self):
        return hash((self.item_id, self.count, self.aux_value))

    def __eq__(self, other):
        # type: (RecipeOutput) -> bool
        if not isinstance(other, RecipeOutput):
            return False
        return (
            self.item_id == other.item_id
            and self.count == other.count
            and self.aux_value == other.aux_value
        )


class CraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.data = data
        self.pattern = data["pattern"]  # type: list[str]
        self.pattern_key = {k: RecipeInput.from_dict(v) for k, v in data["key"].items()}  # type: dict[str, RecipeInput]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]] # type: list[RecipeOutput]

    def get_items_count(self):
        # type: () -> list[RecipeInput]
        new_pk = {k: v.copy() for k, v in self.pattern_key.items()}
        pattern_chars = [c for ln in self.pattern for c in ln if c != " "]
        for p in self.pattern_key:
            new_pk[p].count = pattern_chars.count(p) * self.pattern_key[p].count
        return list(new_pk.values())

    def __hash__(self):
        return hash((tuple(self.pattern), tuple(self.pattern_key.values()), tuple(self.result)))

    def __eq__(self, other):
        # type: (CraftingRecipeRes) -> bool
        if not isinstance(other, CraftingRecipeRes):
            return False
        return (
            self.pattern == other.pattern
            and self.pattern_key == other.pattern_key
            and self.result == other.result
        )


class UnorderedCraftingRecipeRes:
    def __init__(self, data):
        # type: (dict) -> None
        self.data = data
        self.inputs = [RecipeInput.from_dict(v) for v in data["ingredients"]]
        self.result = [RecipeOutput.from_dict(v) for v in data["result"]]

    def __hash__(self):
        return hash((tuple(self.inputs), tuple(self.result)))

    def __eq__(self, other):
        # type: (UnorderedCraftingRecipeRes) -> bool
        if not isinstance(other, UnorderedCraftingRecipeRes):
            return False
        return (
            self.inputs == other.inputs
            and self.result == other.result
        )


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



