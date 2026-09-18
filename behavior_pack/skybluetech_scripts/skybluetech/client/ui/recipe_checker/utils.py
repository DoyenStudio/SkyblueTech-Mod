# coding=utf-8
from skybluetech_scripts.skybluetech.common.mini_jei import RecipeBase


class RecipeCategoriesData:
    def __init__(self, categories_data):
        # type: (list[RecipePageData]) -> None
        self.categories_data = categories_data
        self.looking_category_index = 0
        self.category_index_start = 0

    def categories_num(self):
        return len(self.categories_data)


class RecipePageData:
    def __init__(self, icon_id, recipe_title, recipes):
        # type: (str, str, list[RecipeBase]) -> None
        self.icon_id = icon_id
        self.recipe_title = recipe_title
        self.recipes = recipes
        self.current_page = 0
        self.total_pages_num = 0
        self.recipes_per_page = 0

    def set_page(self, page):
        # type: (int) -> None
        self.current_page = page

    def get_page(self):
        return self.current_page
