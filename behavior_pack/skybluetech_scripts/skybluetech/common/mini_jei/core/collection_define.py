# # coding=utf-8
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar
from .define import RecipeBase, Input

T = TypeVar("T", bound=tuple)
RT = TypeVar("RT", bound=RecipeBase)


# class RecipeCollection(Generic[T, RT]):
#     def __init__(self):
#         # type: () -> None
#         self.recipes = {}  # type: dict[T, list[RT]]

#     def add_recipes(self, *recipes):
#         # type: (RT) -> None
#         for recipe in recipes:
#             self.recipes.setdefault(recipe.key, []).append(recipe)

#     def get_recipe(self, key):
#         # type: (T) -> RT
#         raise NotImplementedError


# def GenerateKey(
#     inputs,  # type: dict[str, dict[int, Input]]
#     shaped=False,  # type: bool
# ):

#     if shaped:
#         return tuple(
#             sorted(
#                 (
#                     (
#                         category,
#                         tuple(sorted(inputs.items(), key=lambda x: x[0])),
#                     )
#                     for category, inputs in inputs.items()
#                 ),
#                 key=lambda x: x[0],
#             )
#         )
#     else:
#         return tuple(
#             sorted(
#                 (
#                     (
#                         category,
#                         tuple(sorted(inputs.values(), key=lambda x: x.id)),
#                     )
#                     for category, inputs in inputs.items()
#                 ),
#                 key=lambda x: x[0],
#             )
#         )


class RecipesCollection(Generic[RT]):
    _registered_collections = {}  # type: dict[str, RecipesCollection]

    def __init__(self, collection_name, *recipes):
        # type: (str, RT) -> None
        self.collection_name = collection_name
        self._recipes = list(recipes)
        self._recipes_mapping = {}  # type: dict[tuple, RT]

        from .register import RegisterRecipe

        for recipe in self._recipes:
            RegisterRecipe(recipe)

        RecipesCollection._registered_collections[collection_name] = self

    def add_recipe(self, recipe):
        # type: (RT) -> None
        self._recipes.append(recipe)

    def remove_recipe(self, recipe):
        # type: (RT) -> None
        self._recipes.remove(recipe)

    def check_recipe(self, collection_key):
        # type: (tuple) -> RT | None
        "WIP"
        if not self._recipes_mapping:
            self._recipes_mapping = {
                recipe.collection_key: recipe for recipe in self._recipes
            }
        return self._recipes_mapping.get(collection_key)

    @classmethod
    def get_collection(cls, collection_name):
        # type: (str) -> RecipesCollection[RecipeBase]
        return cls._registered_collections[collection_name]

    def list(self):
        return self._recipes[:]

    def __getitem__(self, index):
        # type: (int) -> RT
        return self._recipes[index]

    def __iter__(self):
        return iter(self._recipes)

    def __len__(self):
        return len(self._recipes)
