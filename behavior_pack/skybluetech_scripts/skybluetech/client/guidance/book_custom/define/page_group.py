# coding=utf-8
if 0:
    from .base_page import BasePage


class PageGroup(object):
    def __init__(self, pages):
        # type: (list[BasePage]) -> None
        self.pages = pages
        self.parent = None
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

    def __repr__(self):
        return "PageGroup(%s)" % str(self.pages)
