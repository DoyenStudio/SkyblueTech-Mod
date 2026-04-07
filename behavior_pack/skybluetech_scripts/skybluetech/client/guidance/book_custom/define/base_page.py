# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl

if 0:
    from .page_group import PageGroup

pages = {}  # type: dict[str, BasePage]


class BasePage(object):
    ctrl_def_name = "BAD_CTRL"  # type: str

    def __init__(self, page_id=""):
        # type: (str) -> None
        self.page_id = page_id
        self.page_group = None
        pages[page_id] = self

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        pass

    def GetId(self):
        return self.page_id

    def GetGroup(self):
        # type: () -> PageGroup | None
        return None

    def SetGroup(self, group):
        # type: (PageGroup) -> None
        self.page_group = group

    def __repr__(self):
        return 'Page("%s")' % self.page_id
