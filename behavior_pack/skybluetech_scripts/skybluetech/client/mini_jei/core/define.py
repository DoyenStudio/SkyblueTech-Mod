# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar
from skybluetech_scripts.skybluetech.common.mini_jei import RecipeBase


if 0:
    import typing  # noqa: F401


class RecipeRenderer(object):
    recipe_icon_id = "minecraft:barrier"
    render_ui_def_name = "???"
    minijei_title = None  # type: str | None

    def __init__(self, recipe):
        # type: (RecipeBase) -> None
        self.recipe = recipe

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        """
        在页面渲染初始化时执行一次, 用于渲染配方。 传入配方页控件。
        """
        pass

    def RenderUpdate(self, panel_ctrl, render_ticks):
        # type: (UBaseCtrl, int) -> None
        """
        0.2 秒触发一次。render_ticks 每次比上一次触发多 5。
        用于渲染页的持续更新, 如物品轮播, 进度条增加。
        """
        pass

    def DeRender(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        """
        在页面销毁时执行一次, 用于销毁配方。 传入配方页控件。
        """
        pass

    @property
    def cls_name(self):
        return self.__class__.__name__


# class Description(RecipeRenderer):
#     recipe_icon_id = "skybluetech:description_icon"
#     render_ui_def_name = "RecipeCheckerLib.description_page"

#     def __init__(self, categories_with_ids, title, content):


#     def RenderInit(self, panel_ctrl):
#         # type: (UBaseCtrl) -> None
#         panel_ctrl["bg_img/title"].asLabel().SetText(self.title, sync_size=True)
#         panel_ctrl["bg_img/content"].asLabel().SetText(self.content, sync_size=True)


#     def __hash__(self):
#         return hash(self.title)
