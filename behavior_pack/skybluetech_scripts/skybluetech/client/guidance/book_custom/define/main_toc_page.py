# coding=utf-8
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define.page_group import (
    PageGroup,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from .base_page import BasePage

if 0:
    from .page_group import PageGroup


class MainTOCPageSection(object):
    def __init__(self, icon_item_id, icon_item_aux, title, link_to):
        # type: (str, int, str, PageGroup) -> None
        self.icon_item_id = icon_item_id
        self.icon_item_aux = icon_item_aux
        self.title = title
        self.link_to = link_to


class MainTOCPage(BasePage):
    ctrl_def_name = "GuidanceLib.main_toc_page"

    def __init__(self, page_id, sections):
        # type: (str, list[MainTOCPageSection]) -> None
        BasePage.__init__(self, page_id)
        self.sections = sections

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        grid = ctrl["sections_grid"].asGrid()
        grid.SetPropertyBag({"#maximum_grid_items": len(self.sections)})

        def after():
            for i, section in enumerate(self.sections):

                def get_handler(index):
                    def handler(_):
                        self.on_select_section(index)

                    return handler

                e = grid["main_toc_section%d" % (i + 1)]
                e["icon_item_renderer"].asItemRenderer().SetUiItem(
                    Item(section.icon_item_id, section.icon_item_aux)
                )
                e["label"].asLabel().SetText(section.title)
                e["click_btn"].asButton().SetCallback(get_handler(i))

        grid.ExecuteAfterUpdate(after)

    def on_select_section(self, index):
        # type: (int) -> None
        from ....ui.guidance.guidance_ui import GuidanceUI

        ui = GuidanceUI.get_instance()
        if ui is not None:
            ui.load_new_pages(self.sections[index].link_to)

    def SetGroup(self, group):
        # type: (PageGroup) -> None
        for s in self.sections:
            s.link_to.SetParent(group)
        BasePage.SetGroup(self, group)

    def __repr__(self):
        return "MainTOCPage(%s)" % str([s.link_to for s in self.sections])
