# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl

if 0:
    from .page_group import PageGroup


class BasePage(object):
    ctrl_def_name = "BAD_CTRL"  # type: str

    def __init__(self):
        # type: () -> None
        self.page_group = None

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        pass

    def ScreenTicking(self):
        pass

    def GetGroup(self):
        # type: () -> PageGroup | None
        return None

    def SetGroup(self, group):
        # type: (PageGroup) -> None
        self.page_group = group
