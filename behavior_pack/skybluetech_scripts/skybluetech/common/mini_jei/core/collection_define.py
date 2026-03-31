# # coding=utf-8
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar
from .define import Recipe, Input

T = TypeVar("T", bound=tuple)
RT = TypeVar("RT", bound=Recipe)


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
    def __init__(self, collection_name, *recipes):
        # type: (str, RT) -> None
        self.collection_name = collection_name
        self._recipes = list(recipes)

    def add_recipe(self, recipe):
        # type: (RT) -> None
        self._recipes.append(recipe)

    def remove_recipe(self, recipe):
        # type: (RT) -> None
        self._recipes.remove(recipe)

    def list(self):
        return self._recipes[:]

    def __iter__(self):
        return iter(self._recipes)

    def __len__(self):
        return len(self._recipes)
