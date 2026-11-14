# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.mini_jei.common.description import (
    SourceDescription,
    UsageDescription,
)
from ..core import RecipeRenderer


class DescriptionRenderer(RecipeRenderer):
    recipe_icon_id = "skybluetech:description_icon"
    render_ui_def_name = "RecipeCheckerLib.description_page"

    def __init__(self, desc):
        # type: (SourceDescription | UsageDescription) -> None
        super(DescriptionRenderer, self).__init__(desc)
        self.desc = desc

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        panel_ctrl["bg_img/title"].asLabel().SetText(self.desc.title, sync_size=True)
        panel_ctrl["bg_img/content"].asLabel().SetText(
            self.desc.content, sync_size=True
        )


SourceDescription.SetRenderer(DescriptionRenderer)
UsageDescription.SetRenderer(DescriptionRenderer)
