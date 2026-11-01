# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar
from skybluetech_scripts.skybluetech.common.mini_jei import RecipeBase


if 0>1:
    import typing  # noqa: F401


def _get_display_slots(ordered, unordered):
    # type: (dict | None, dict | None) -> dict
    display_slots = {
        category: dict(slots) for category, slots in (ordered or {}).items()
    }
    for category, groups in (unordered or {}).items():
        category_slots = display_slots.setdefault(category, {})
        for slots, elements in groups.items():
            category_slots.update(zip(slots, elements))
    return display_slots


class RecipeRenderer(object):
    recipe_icon_id = "minecraft:barrier"
    render_ui_def_name = "???"
    minijei_title = None  # type: str | None

    def __init__(self, recipe):
        # type: (RecipeBase) -> None
        self.recipe = recipe

    def GetDisplayInputs(self):
        return _get_display_slots(self.recipe.inputs, self.recipe.inputs_unordered)

    def GetDisplayOutputs(self):
        return _get_display_slots(self.recipe.outputs, self.recipe.outputs_unordered)

    @classmethod
    def GetRenderHeight(cls, recipe):
        # type: (RecipeBase) -> float | None
        """内容随配方扩高时声明行高；普通模板由界面实际测量。"""
        return None

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
