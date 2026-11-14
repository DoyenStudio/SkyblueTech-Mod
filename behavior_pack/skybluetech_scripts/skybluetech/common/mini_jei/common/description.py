# coding=utf-8
from ..core import RecipeBase, RegisterRecipe


class SourceDescription(RecipeBase):
    recipe_icon_id = "skybluetech:description_icon"

    def __init__(self, categories_with_ids, title, content):
        # type: (dict[str, list[str]], str, str) -> None
        self.categories_with_ids = categories_with_ids
        self.title = title
        self.content = content

    def GetInputs(self):
        return {}

    def GetOutputs(self):
        return self.categories_with_ids

    def __hash__(self):
        return hash(self.title)


class UsageDescription(SourceDescription):
    def GetInputs(self):
        return self.categories_with_ids

    def GetOutputs(self):
        return {}


def RegisterSourceDescription(categories_with_ids, title, content):
    # type: (dict[str, list[str]], str, str) -> None
    """
    注册仅在来源查询中显示的描述。

    Args:
        categories_with_ids (dict[str, list[str]]): 被描述物分组: 分组内被描述物列表
        title (str): 标题
        content (str): 正文内容
    """
    RegisterRecipe(
        SourceDescription(
            categories_with_ids,
            title,
            content,  # .replace(" ", py2_unicode("\u00a0"))
        )
    )


def RegisterUsageDescription(categories_with_ids, title, content):
    # type: (dict[str, list[str]], str, str) -> None
    """
    注册仅在用途查询中显示的描述。

    Args:
        categories_with_ids (dict[str, list[str]]): 被描述物分组: 分组内被描述物列表
        title (str): 标题
        content (str): 正文内容
    """
    RegisterRecipe(UsageDescription(categories_with_ids, title, content))
