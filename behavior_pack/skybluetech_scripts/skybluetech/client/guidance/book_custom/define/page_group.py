# coding=utf-8
if 0:
    from .base_page import BasePage

page_groups = {}  # type: dict[str, PageGroup]


class PageGroup(object):
    def __init__(self, id, pages):
        # type: (str, list[BasePage]) -> None
        self.id = id
        self.pages = pages
        self.parent = None
        page_groups[id] = self
        for page in pages:
            page.SetGroup(self)

    def GetPages(self):
        # type: () -> list[BasePage]
        return self.pages

    def GetPagesNum(self):
        return len(self.pages)

    def GetParent(self):
        # type: () -> PageGroup | None
        return self.parent

    def SetParent(self, parent):
        # type: (PageGroup) -> None
        self.parent = parent

    def FastJump(self, index=0):
        # type: (int) -> None
        from ....ui.guidance.guidance_ui import GuidanceUI

        ui = GuidanceUI.get_instance()
        if ui is not None:
            ui.load_new_pages(self, index)

    def __repr__(self):
        return "PageGroup(%s)" % str(self.pages)


def GetPageGroup(id):
    # type: (str) -> PageGroup | None
    return page_groups.get(id)
