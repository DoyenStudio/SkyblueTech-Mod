# coding=utf-8
from .define import RecipeBase

recipesFrom = {}  # type: dict[str, dict[str, list[RecipeBase]]]
"根据输出查找配方"
recipesTo = {}  # type: dict[str, dict[str, list[RecipeBase]]]
"根据输入查找配方"
recipesOf = {}  # type: dict[str, list[RecipeBase]]
"根据配方类型查找配方"
